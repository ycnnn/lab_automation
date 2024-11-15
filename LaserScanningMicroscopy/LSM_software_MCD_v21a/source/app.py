import sys
import os
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QGuiApplication, QFontDatabase, QFont, QColor, QPixmap
from PySide6.QtCore import Qt, QByteArray, QBuffer, QLoggingCategory
import pyqtgraph as pg
import numpy as np
from decimal import Decimal
import base64
import warnings

warnings.filterwarnings("ignore", module="pyqtgraph")
warnings.filterwarnings("ignore", module="PySide6")

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
    def __init__(self, title):
        super().__init__()
        
        self.setWindowTitle(title)

        self.linewidth = 0
        self.scan_num = 0
        self.x_offset = 0
        
        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Create a layout
        self.layout = QVBoxLayout()
        
    
        self.central_widget.setLayout(self.layout)
        self.central_widget.setStyleSheet("background-color: black;")

       
        self.chart_widget = pg.PlotWidget()
        self.img_widget = pg.PlotWidget()
        self.info_label = QLabel('Currently scanning line 0')
        self.xy_label = QLabel('X position = 0, Y position = 0')
        

        
        
        
        self.layout.setSpacing(0)
        

        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.xy_label)
        self.layout.addWidget(self.chart_widget)
        self.layout.addWidget(self.img_widget)

        widget_format(self.chart_widget)
        widget_format(self.img_widget)

        self.img_widget.mousePressEvent = self.on_click

        # self.img.getPlotItem().getViewBox().boundingRect()
        # self.img.getPlotItem().getAxis('bottom').geometry()
        # self.img.getPlotItem().getAxis('bottom').geometry()
        # self.img.getPlotItem().getViewBox().map

        

    def on_click(self, event):
        # Get the coordinates of the click inside the image
        pos = event.pos()
        scene_pos = self.img_widget.getPlotItem().getViewBox().mapToView(pos)
        # scene_pos = self.img.getPlotItem().getAxis('top').mapToView(pos)
        x, y = scene_pos.x(), scene_pos.y()
        self.location = (x, y)
        # getCoords: Extracts the position of the rectangle’s top-left corner to *``x1`` and *``y1``, and the position of the bottom-right corner to *``x2`` and *``y2``
        # The detailed info about the box coordinates helps us to calculate the position of mouse click
        # view_box_coords = self.img_widget.getPlotItem().getViewBox().boundingRect().getCoords()
        top_axis_coords = self.img_widget.getPlotItem().getAxis('top').geometry().getCoords()
        # left_axis_coords = self.img_widget.getPlotItem().getAxis('left').geometry().getCoords()
        if self.x_offset == 0:
            self.x_offset = self.linewidth *  top_axis_coords[0] / (top_axis_coords[2] - top_axis_coords[0])

        x_label = int(x - self.x_offset)
        y_label = int(self.scan_num - y)

        # Update the textbox with the coordinates
        self.xy_label.setText(f"X position = {x_label}, Y position = {y_label}")

        # print('\n\n\n\n\n\n\n\n')
        # print('Viewbox size: ')
        # print(self.img.getPlotItem().getViewBox().boundingRect().getCoords())
        # print('\n\n')
        # print('Top axis:')
        # print(self.img.getPlotItem().getAxis('top').geometry().getCoords())
        # print('\n\n')
        # print('Bottom axis:')
        # print(self.img.getPlotItem().getAxis('bottom').geometry().getCoords())
        # print('Left axis:')
        # print(self.img.getPlotItem().getAxis('left').geometry().getCoords())
        # print('\n\n')
        # print('Right axis:')
        # print(self.img.getPlotItem().getAxis('right').geometry().getCoords())
        # print('\n\n\n\n\n\n\n\n')


class QPlot:

    def __init__(self, 
                 line_width, 
                 scan_num,
                 channel_num,
                 window_width_min,
                 window_width_max,
                 show_zero_level,
                 font_size,
                 channel_names,
                 axis_label_ticks_distance=10,
                 text_bar_height=20) -> None:

        self.app = QApplication(sys.argv)
        self.font_size = font_size

        
        font_family = load_font('font/SourceCodePro-Medium.ttf')
        
        
        if font_family:
            global_font = QFont(font_family)
            global_font.setPixelSize(self.font_size)
            self.app.setFont(global_font)

        self.counter = 0
        self.time = time.time()
        self.screen_width, self.screen_height = self.app.primaryScreen().size().toTuple()
        self.line_width = line_width
        self.scan_num = int(scan_num/2)
        self.windows = []
        self.charts = []
        self.imgs = []
        self.info_labels = []
        self.channel_num = channel_num
        self.channel_names = channel_names
        self.axis_label_ticks_distance = axis_label_ticks_distance





        self.window_width = min(window_width_max, 
                                max(window_width_min,self.screen_width/(1+self.channel_num)))
        self.window_height = self.window_width
        self.window_distance = self.screen_width/(1+self.channel_num)

        self.chart_height = self.window_height/2.5
        character_aspect_ratio = 0.5

        self.axis_tick_label_width = 7 * self.font_size * character_aspect_ratio + self.axis_label_ticks_distance

        self.img_height = min(
            max(
                50, 
                (self.window_width - self.axis_tick_label_width) * self.scan_num/self.line_width),

            self.screen_height * 0.9)
        
        
        self.img_height = min(self.img_height, self.screen_height *0.8)
        

        self.label_height = text_bar_height
        self.total_width_scaling_factor = 1.08
        self.total_height_scaling_factor = 1.08
        self.axis_label_ticks_distance = axis_label_ticks_distance

        self.total_width = self.total_width_scaling_factor*self.window_width
        self.total_height = self.total_height_scaling_factor*(5 + self.chart_height + self.img_height + self.label_height)






        self.data = np.zeros(shape=(self.channel_num, self.line_width, self.scan_num))
        self.retrace_data = np.zeros(shape=(self.channel_num, self.line_width, self.scan_num))

        self.show_zero_level = show_zero_level
        
        for channel_id in range(self.channel_num):
            
            temp_window = SubWindow(title=f'Channel {channel_id}')

            temp_window.scan_num = self.scan_num
            temp_window.linewidth = self.line_width
           
            temp_window.show()
            self.windows.append(temp_window)

            chart = temp_window.chart_widget.plot(self.data[channel_id,:,0])


            temp_window.chart_widget.getViewBox().setDefaultPadding(padding=0.1)
            temp_window.chart_widget.getViewBox().enableAutoRange(pg.ViewBox.XAxis, False)

            
            zero_line = pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen('r', width=2, style=Qt.DashLine))

            y_axis = CustomAxisItem(orientation='left',
                                     axis_label_ticks_distance=self.axis_label_ticks_distance)
            img_y_axis = CustomAxisItem(orientation='left',
                                        axis_label_ticks_distance=self.axis_label_ticks_distance)

            # Replace the default y-axis with the custom axis for both the cart and the image
            temp_window.chart_widget.setAxisItems({'left': y_axis})
            temp_window.img_widget.setAxisItems({'left': img_y_axis})

            # Set the color of y tick labels in the chart 
            # color_for_chart_axis_tick_label = QColor(0, 0, 0, 0)
            temp_window.chart_widget.getAxis('left').setTextPen('white')

            # Hide the y axis of the image 
            transparent_color_for_img_axis_tick_label = QColor(0, 0, 0, 0)
            temp_window.img_widget.getAxis('left').setTextPen(transparent_color_for_img_axis_tick_label)
            if self.show_zero_level:
                temp_window.chart_widget.addItem(zero_line)

            img = pg.ImageItem(self.data[channel_id])
            temp_window.img_widget.addItem(img)

            self.charts.append(chart)
            self.imgs.append(img)
            self.info_labels.append(temp_window.info_label)

            

        # Move windows around, and set the size of each window
        for channel_id in range(self.channel_num):
            self.windows[channel_id].info_label.setFixedHeight(self.label_height)

            self.windows[channel_id].chart_widget.setFixedSize(self.window_width, self.chart_height)
            
            self.windows[channel_id].img_widget.setFixedSize(self.window_width, self.img_height)

            self.windows[channel_id].setFixedSize(self.total_width, self.total_height)
            self.windows[channel_id].move(self.window_distance*channel_id, 0)

    def update(self, fetched_data):
        
        
        self.data[:,:,self.scan_num - self.counter - 1] = fetched_data
        self.counter += 1
        elapse_time = time.time() - self.time
        self.time = time.time()
        self.remaining_time = int(elapse_time*(self.scan_num - self.counter))

        for row_id in range(self.channel_num):
            self.windows[row_id].setWindowTitle(self.channel_names[row_id])

            self.charts[row_id].setData(fetched_data[row_id])

            self.imgs[row_id].setImage(self.data[row_id])
            self.info_labels[row_id].setText(f'Scanning line {self.counter}/{self.scan_num}' + f', {self.remaining_time} s remaining')
            
        
        QApplication.processEvents()
    
    def retrace_update(self, fetched_data):
        # print('Self data shape is')
        # print(self.data.shape)

        self.retrace_data[:,:,self.scan_num - self.counter - 1] = fetched_data

        # self.setWindowTitle(f'{self.channel_num} Channel Scan: Frame {self.counter}, Est time {self.remaining_time} s')
        QApplication.processEvents()

    def turn_image_to_base64(self, img):
        # Save QImage to a QByteArray
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QBuffer.WriteOnly)
        img.save(buffer, "PNG")

        # Convert QByteArray to base64 string
        image_base64 = base64.b64encode(byte_array.data()).decode('utf-8')

        return image_base64

    def save_screenshot(self, filepath=None, fileformat='png'):
        self.screenshots = []
        for channel_id in range(self.channel_num):
            img = self.windows[channel_id].grab(self.windows[channel_id].rect()).toImage()
            image_base64 = self.turn_image_to_base64(img)
            self.screenshots.append(image_base64)





if __name__ == "__main__":
    channel_num = 10
    line_width = 90
    scan_num= 2

    app = QPlot(channel_num=channel_num, line_width=line_width, scan_num=scan_num)
    app.app.exec()
 
