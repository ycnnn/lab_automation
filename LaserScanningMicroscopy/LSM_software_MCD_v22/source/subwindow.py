import sys
import os
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLabel,QPushButton
from PySide6.QtGui import QGuiApplication, QFontDatabase, QFont, QColor, QPixmap, QPen
from PySide6.QtCore import Qt, QByteArray, QBuffer, QLoggingCategory, QThread, Signal,QRectF
import pyqtgraph as pg
import numpy as np
from decimal import Decimal
import base64
import warnings
from source.params.position_params import Position_parameters
from source.params.scan_params import Scan_parameters
from source.params.display_params import Display_parameters
from source.scan_process import LSM_scan
import source.inst_driver as inst_driver



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
    def __init__(self, scan_num, line_width, channel_id=0, title=None, window_width=400, axis_label_distance=10, font_size=12, position_parameters=None, thread=None):
        super().__init__()

        self.channel_id = channel_id
        self.position_parameters = position_parameters
       
        self.title = title if title else f'Channel {channel_id}'
        self.setWindowTitle(self.title)
        self.scan_num, self.line_width = (scan_num, line_width)
        self.count = None
        self.data = np.zeros((self.scan_num, self.line_width))
        self.thread = thread
        

        
        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Create a layout
        self.layout = QVBoxLayout()
        
    
        self.central_widget.setLayout(self.layout)
        self.central_widget.setStyleSheet("background-color: black;")

        self.button = QPushButton("Terminate", self)

        self.button.setStyleSheet("""
            QPushButton {
                background-color: red;  /* Red background */
                border: 0px solid black;  /* Black border */
                color: white;  /* White text color */
           
                padding: 5px;  /* Padding inside the button */
            }
            QPushButton:hover {
                background-color: darkred;  /* Dark red when hovered */
            }
        """)
                
        self.chart_widget = pg.PlotWidget()
        self.img_widget = pg.PlotWidget()
        self.info_label = QLabel('Currently scanning line 0')
        self.xy_label = QLabel('X position = 0, Y position = 0')
        
        self.layout.setSpacing(0)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.set_terminate_flag)
        self.thread.finished.connect(self.finish)

        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.xy_label)
        self.layout.addWidget(self.chart_widget)
        self.layout.addWidget(self.img_widget)

        # self.img_widget.mousePressEvent = self.on_click
        self.proxy = pg.SignalProxy(self.img_widget.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)

        self.curve = self.chart_widget.plot()
        self.img = pg.ImageItem(self.data.T)
        self.img_widget.addItem(self.img)


        self.roi = pg.ROI([0, 0], [self.line_width,self.scan_num], pen='r', maxBounds=QRectF(0,0,self.line_width,self.scan_num))  # Initial position and size
        self.roi.addScaleHandle([1, 1], [0, 0])  # Add scaling handles
        self.roi.addScaleHandle([0, 0], [1, 1])
        self.roi.addScaleHandle([0, 1], [1, 0])
        self.roi.addScaleHandle([1, 0], [0, 1])
        self.img_widget.addItem(self.roi)
        self.roi.sigRegionChanged.connect(self.updateROI)

        self.roi_x_range = (0, self.line_width)
        self.roi_y_range = (0, self.scan_num)

        self.time = time.time()
        self.remaining_time = 0

        self.window_width = window_width
        self.axis_label_distance = axis_label_distance
        self.font_size = font_size
        self.ui_format()

    def set_terminate_flag(self):
        # print('\n\n\n')
        # print('Terminate!')
        # print('\n\n\n')
        self.thread.is_terminated = True

    def ui_format(self):

        widget_format(self.chart_widget)
        widget_format(self.img_widget)

        y_axis = CustomAxisItem(orientation='left',
                                     axis_label_ticks_distance=self.axis_label_distance)
        img_y_axis = CustomAxisItem(orientation='left',
                                    axis_label_ticks_distance=self.axis_label_distance)
        transparent_color_for_img_axis_tick_label = QColor(0, 0, 0, 0)
        # Replace the default y-axis with the custom axis for both the cart and the image
        self.chart_widget.setAxisItems({'left': y_axis})
        self.img_widget.setAxisItems({'left': img_y_axis})
        self.chart_widget.getAxis('left').setTextPen('white')
        self.img_widget.getAxis('left').setTextPen(transparent_color_for_img_axis_tick_label)
        self.img.getViewBox().invertY(True)

        
        self.chart_widget.setFixedHeight(100)
        self.img_widget.setAspectLocked(False)
        x_axis_offset = self.img_widget.getPlotItem().getAxis('top').geometry().getCoords()[0]
        self.chart_widget.setFixedSize(self.window_width, max(100, self.window_width/3))
        self.img_widget.setFixedSize(self.window_width, (self.window_width-x_axis_offset) * self.scan_num/self.line_width)


    
    def mouse_moved(self, event):
      
        self.axis_label_offset_calculated = False
        scene_pos = self.img_widget.getPlotItem().getViewBox().mapToView(event[0])
     
        x, y = scene_pos.x(), scene_pos.y()
        self.location = (x, y)

        if not self.axis_label_offset_calculated:
            top_axis_coords = self.img_widget.getPlotItem().getAxis('top').geometry().getCoords()
            right_axis_coords = self.img_widget.getPlotItem().getAxis('right').geometry().getCoords()
            view_range = self.img_widget.getPlotItem().getViewBox().viewRange()
            self.x_range, self.y_range = (view_range[0][1] - view_range[0][0], view_range[1][1] - view_range[1][0])
            self.x_offset = self.x_range *  top_axis_coords[0] / (top_axis_coords[2] - top_axis_coords[0])
            self.y_offset = self.y_range *  right_axis_coords[1] / (right_axis_coords[3] - right_axis_coords[1])

        x_label = int(x - self.x_offset)
        y_label = int(self.scan_num - (y - self.y_offset))

        x_label = max(0, min(x_label, self.line_width - 1))
        y_label = max(0, min(y_label, self.scan_num - 1))

        x_pos = self.position_parameters.x_coordinates[y_label, x_label]
        y_pos = self.position_parameters.y_coordinates[y_label, x_label]

        # Update the textbox with the coordinates
        self.xy_label.setText(f"X position = {x_pos:.1f}, Y position = {y_pos:.1f}")

    def updateROI(self):

        roi_pos = (self.roi.pos().x(), self.roi.pos().y())
        roi_size = (self.roi.size().x(), self.roi.size().y())
        self.roi_x_range = (int(roi_pos[0]), int(roi_pos[0]) + int(roi_size[0]))
        self.roi_y_range = (int(roi_pos[1]), int(roi_pos[1]) + int(roi_size[1]))

        self.rescale_color()

    def update_plot(self, data_pack):
        self.count, new_data = data_pack
        self.data[self.count] = new_data[self.channel_id]
        
        elapse_time = time.time() - self.time
        if self.count >= 1:
            self.remaining_time = int(elapse_time / self.count * (self.scan_num - self.count))

        self.curve.setData(self.data[self.count])
        self.img.setImage(self.data.T)
        self.rescale_color()
        self.info_label.setText(f'Currently scanning line {int(self.count)}, ' + f'{self.remaining_time} s remaining')

        if self.count == self.scan_num - 1:
            self.pixmap = self.grab()

    def rescale_color(self):
        data = self.data.T[self.roi_x_range[0]:self.roi_x_range[1], self.roi_y_range[0]:self.roi_y_range[1]]
        plot_max_val = np.max(data)
        plot_min_val = np.min(data)
        self.img.setLevels((plot_min_val, plot_max_val))

    def finish(self):
        # When the thread finishes, change the button's text and color
        self.button.setText("Scan finished")
        self.button.setStyleSheet("""
            QPushButton {
                background-color: green;  /* Red background */
                border: 0px solid black;  /* Black border */
                color: white;  /* White text color */
           
                padding: 5px;  /* Padding inside the button */
            }
            QPushButton:hover {
                background-color: green;  /* Dark red when hovered */
            }
        """)
    

if __name__ == "__main__":
    pass