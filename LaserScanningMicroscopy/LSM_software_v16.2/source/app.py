import sys
import os
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QGuiApplication, QFontDatabase, QFont
from PySide6.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from decimal import Decimal

def load_font(font_path):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    font_id = QFontDatabase.addApplicationFont(dir_path + '/' +  font_path)
    if font_id == -1:
        print(f"Failed to load font from {font_path}")
        return None
    font_families = QFontDatabase.applicationFontFamilies(font_id)
    if not font_families:
        print(f"No font families found for {font_path}")
        return None
    return font_families[0]




def widget_format(widget):
    widget.hideButtons()
    widget.setMouseEnabled(x=False, y=False)
    widget.setStyleSheet("background-color: black;")
    # widget.setXRange(0, x_range, padding=0)
    widget.setDefaultPadding(0)

    for axis_label in ['left', 'right', 'bottom', 'top']:
        widget.showAxis(axis_label)
        widget.getAxis(axis_label).setTicks([])
        widget.getAxis(axis_label).setStyle(tickLength=2,showValues=False)
      


class SubWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        
        self.setWindowTitle(title)
        
        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Create a layout
        self.layout = QVBoxLayout()
        
    
        self.central_widget.setLayout(self.layout)
        self.central_widget.setStyleSheet("background-color: black;")

       
        self.chart = pg.PlotWidget()
        self.img = pg.PlotWidget()
        self.info_label = QLabel('Currently scanning line 0')
        self.top_label = QLabel('Plot Max = 0.0')
        self.bot_label = QLabel('Plot Min = 0.0')
        

        
        
        
        self.layout.setSpacing(0)
        

        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.top_label)
        self.layout.addWidget(self.chart)
        self.layout.addWidget(self.bot_label)
        self.layout.addWidget(self.img)

        widget_format(self.chart)
        widget_format(self.img)


class QPlot:

    def __init__(self, 
                 line_width, 
                 scan_num,
                 channel_num,
                 window_width_min,
                 window_width_max,
                 show_zero_level,
                 text_bar_height=20) -> None:

        self.app = QApplication(sys.argv)

        
        font_family = load_font('font/SourceCodePro-Medium.ttf')
        
        if font_family:
            self.app.setFont(QFont(font_family))

        self.counter = 0
        self.time = time.time()
        self.screen_width, self.screen_height = self.app.primaryScreen().size().toTuple()
        self.line_width = line_width
        self.scan_num = int(scan_num/2)
        self.windows = []
        self.charts = []
        self.imgs = []
        self.info_labels = []
        self.top_labels = []
        self.bot_labels = []
        self.viewranges = []
        self.channel_num = channel_num
        self.window_width = min(window_width_max, 
                                max(window_width_min,self.screen_width/(1+self.channel_num)))
        self.window_height = self.window_width
        self.window_distance = self.screen_width/(1+self.channel_num)
        self.chart_height = self.window_height/2.5
        self.img_height = max(50, self.window_width * self.scan_num/self.line_width)
        self.label_height = text_bar_height
        self.total_width_scaling_factor = 1.08
        self.total_height_scaling_factor = 1.08

        self.total_width = self.total_width_scaling_factor*self.window_width
        self.total_height = self.total_height_scaling_factor*(self.chart_height + self.img_height + 3 * self.label_height)

        self.data = np.zeros(shape=(self.channel_num, self.line_width, self.scan_num))
        self.retrace_data = np.zeros(shape=(self.channel_num, self.line_width, self.scan_num))

        self.show_zero_level = show_zero_level
        
        for channel_id in range(self.channel_num):
            
            temp_window = SubWindow(title=f'Channel {channel_id}')
           
            temp_window.show()
            self.windows.append(temp_window)

            chart = temp_window.chart.plot(self.data[channel_id,:,0])
            zero_line = pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen('r', width=2, style=Qt.DashLine))
            if self.show_zero_level:
                temp_window.chart.addItem(zero_line)

            img = pg.ImageItem(self.data[channel_id])
            temp_window.img.addItem(img)

            self.charts.append(chart)
            self.imgs.append(img)
            self.viewranges.append([chart.getViewBox().viewRange()])
            self.info_labels.append(temp_window.info_label)
            self.top_labels.append(temp_window.top_label)
            self.bot_labels.append(temp_window.bot_label)

            

        # Move windows around, and set the size of each window
        for channel_id in range(self.channel_num):
            self.windows[channel_id].info_label.setFixedHeight(self.label_height)
            self.windows[channel_id].top_label.setFixedHeight(self.label_height)
            self.windows[channel_id].bot_label.setFixedHeight(self.label_height)

            self.windows[channel_id].chart.setFixedSize(self.window_width, self.chart_height)
            self.windows[channel_id].img.setFixedSize(self.window_width, self.img_height)
            self.windows[channel_id].setFixedSize(self.total_width, self.total_height)
            self.windows[channel_id].move(self.window_distance*channel_id, 0)

    def update(self, fetched_data):
        

        self.data[:,:,self.scan_num - self.counter - 1] = fetched_data
        self.counter += 1
        elapse_time = time.time() - self.time
        self.time = time.time()
        self.remaining_time = int(elapse_time*(self.scan_num - self.counter))

        for row_id in range(self.channel_num):
            self.windows[row_id].setWindowTitle(f'Channel {row_id}, estimated time {self.remaining_time} s')

            self.charts[row_id].setData(fetched_data[row_id])

            new_chart_data_viewrange = self.charts[row_id].getViewBox().viewRange()[1]
            self.top_labels[row_id].setText('Plot Max = ' + f"{Decimal(new_chart_data_viewrange[1]):+.1E}")
            self.bot_labels[row_id].setText('Plot Min = ' + f"{Decimal(new_chart_data_viewrange[0]):+.1E}")

            
            
            


            self.imgs[row_id].setImage(self.data[row_id])
            self.info_labels[row_id].setText(f'Scanning line {self.counter}/{self.scan_num}')
            
        
        QApplication.processEvents()
    
    def retrace_update(self, fetched_data):
        # print('Self data shape is')
        # print(self.data.shape)

        self.retrace_data[:,:,self.scan_num - self.counter - 1] = fetched_data

        # self.setWindowTitle(f'{self.channel_num} Channel Scan: Frame {self.counter}, Est time {self.remaining_time} s')
        QApplication.processEvents()
    
    def save_results(self, filepath=None, fileformat='png'):
        for channel_id in range(self.channel_num):
            img = self.windows[channel_id].grab(self.windows[channel_id].rect())
            img.save(filepath + f'screenshot_channel_{channel_id}.' + fileformat, fileformat)

        # final_data = np.flip(np.array([self.data, self.retrace_data]), axis=(2,3))
        np.save(filepath + 'data/trace_data', self.data)
        np.save(filepath + 'data/retrace_data', self.retrace_data)
        for channel_id in range(self.channel_num):
            np.savetxt(filepath + f'data_text/trace_data_chanel_{channel_id}.csv', 
                       self.data[channel_id], delimiter=',')
            np.savetxt(filepath + f'data_text/retrace_data_chanel_{channel_id}.csv', 
                       self.retrace_data[channel_id], delimiter=',')

           



if __name__ == "__main__":
    channel_num = 10
    line_width = 90
    scan_num= 2

    app = QPlot(channel_num=channel_num, line_width=line_width, scan_num=scan_num)
    app.app.exec()
 
