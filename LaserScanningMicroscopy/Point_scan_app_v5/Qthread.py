import sys
import os
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QGuiApplication, QFontDatabase, QFont, QColor, QPixmap, QPen
from PySide6.QtCore import Qt, QByteArray, QBuffer, QLoggingCategory, QThread, Signal,QRectF
import pyqtgraph as pg
import numpy as np
from decimal import Decimal
import base64
import warnings



class DataThread(QThread):

    data_ready = Signal(list)
    
    def __init__(self, scan_num, line_width, channel_num=2, **kwargs):
        super().__init__()
        self.kwargs = kwargs
        self.count = 0
        self.scan_num = scan_num
        self.channel_num = channel_num

    def run(self):
        while self.count < self.scan_num:
            data = np.random.normal(size=(self.channel_num)) + self.count  # Simulate new data
            self.data_ready.emit([self.count, data])
            self.count += 1
            time.sleep(0.02)  # Simulate processing delay


class CustomAxisItem(pg.AxisItem):
    def __init__(self, axis_label_ticks_distance, *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)
        self.setStyle(tickTextOffset=axis_label_ticks_distance)  # Move tick labels inside
    def tickStrings(self, values, scale, spacing):
        # Generate tick strings with scientific notation, 1 digit after decimal, and always show sign
        return [f"{Decimal(value):+.1E}" for value in values]
        
  

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

    for axis_label in [
        # 'left', 
                       'right', 'bottom', 'top']:
        widget.showAxis(axis_label)
        widget.getAxis(axis_label).setTicks([])
        widget.getAxis(axis_label).setStyle(tickLength=2,showValues=False)
      

class SubWindow(QMainWindow):
    def __init__(self, scan_num, line_width, channel_id=0, title=None, window_width=400, axis_label_distance=10, font_size=12):
        super().__init__()

        self.channel_id = channel_id

        self.setWindowTitle(title if title else f'Channel {channel_id}')
        self.scan_num= (scan_num)
        self.count = None
        self.data = np.zeros(self.scan_num)
        
        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Create a layout
        self.layout = QVBoxLayout()
        
        self.central_widget.setLayout(self.layout)
        self.central_widget.setStyleSheet("background-color: black;")

       
        self.chart_widget = pg.PlotWidget()
        self.info_label = QLabel('Currently scanning line 0')
  
        
        self.layout.setSpacing(0)
        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.chart_widget)
   
        self.curve = self.chart_widget.plot()
      
        self.time = time.time()
        self.remaining_time = 0

        self.window_width = window_width
        self.axis_label_distance = axis_label_distance
        self.font_size = font_size
        self.ui_format()

    def ui_format(self):

        widget_format(self.chart_widget)
        

        y_axis = CustomAxisItem(orientation='left',
                                     axis_label_ticks_distance=self.axis_label_distance)

        # Replace the default y-axis with the custom axis for both the cart and the image
        self.chart_widget.setAxisItems({'left': y_axis})
        self.chart_widget.getAxis('left').setTextPen('white')

    def update_plot(self, data_pack):
        self.count, new_data = data_pack
        self.data[self.count] = new_data[self.channel_id]
        
        elapse_time = time.time() - self.time
        if self.count >= 1:
            self.remaining_time = int(elapse_time / self.count * (self.scan_num - self.count))

        self.curve.setData(self.data)
        self.info_label.setText(f'Currently scanning line {int(self.count)}, ' + f'{self.remaining_time} s remaining')


    

if __name__ == "__main__":

    scan_num, line_width = (100,100)
    channel_num = 3

    app = QApplication([])
    font_family = load_font('font/SourceCodePro-Medium.ttf')
    if font_family:
        global_font = QFont(font_family)
        global_font.setPixelSize(12)
        app.setFont(global_font)



    # Create the shared data thread
    data_thread = DataThread(channel_num=channel_num, scan_num=scan_num, line_width=line_width)

    windows = []
    for channel_id in range(channel_num):
        window = SubWindow(channel_id=channel_id, scan_num=scan_num, line_width=line_width)
        data_thread.data_ready.connect(window.update_plot)
        windows.append(window)



    # Start the data thread
    data_thread.start()

    # Show both windows
    for channel_id in range(channel_num):
        windows[channel_id].show()

    app.exec()

