import sys
import os
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLabel,QPushButton, QProgressBar, QSpacerItem, QSizePolicy,QToolTip
from PySide6.QtGui import QFontDatabase, QColor,QMouseEvent
from PySide6.QtCore import Qt, QRectF, QTimer
import pyqtgraph as pg
import numpy as np
from decimal import Decimal




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
    def __init__(self, 
                 controller, 
                 scan_num, line_width, channel_id=0, title=None, 
                 auto_close_time_in_s=3,
                 show_zero=True,
                 window_width=600, axis_label_distance=10, font_size=12, position_parameters=None, thread=None):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)


        self._is_mouse_pressed = False
        self._mouse_start_pos = None
        self._window_start_pos = None


        self.controller = controller
        self.controller.add_window(self)
        self.show_zero = show_zero
        self.channel_id = channel_id
        self.position_parameters = position_parameters
       
        self.title = title if title else f'Channel {channel_id}'
        self.setWindowTitle(self.title)
        self.scan_num, self.line_width = (scan_num, line_width)
        self.count = None
        self.data = np.zeros((self.scan_num, self.line_width))
        self.thread = thread
        self.auto_close_time_in_s = auto_close_time_in_s

        # self.auto_close_timer = QTimer(self)
        # self.auto_close_timer.setInterval(self.auto_close_time_in_s * 1000)  
        # self.auto_close_timer.timeout.connect(self.close)

        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Create a layout
        self.layout = QVBoxLayout()
        
        
    
        self.central_widget.setLayout(self.layout)
        self.central_widget.setStyleSheet("background-color: black;")

    
        self.button = QPushButton(f"Scanning line %v/{self.scan_num + 1}", self)
        self.button.setStyleSheet("""
            QPushButton {
                
                background-color: black;  /* Red background */
                border: 0px solid black;  /* Black border */
                color: white;  /* White text color */
           
                padding: 5px;  /* Padding inside the button */
            }
            QPushButton:hover {
                background-color: darkred;  /* red when hovered */
            }
        """)
                
        self.chart_widget = pg.PlotWidget()
        self.img_widget = pg.PlotWidget()
        self.info_label = QLabel(self.title + ' \nClick the progress bar to terminate')
        self.xy_label = QLabel('Move the mouse to read the location')
        
        self.layout.setSpacing(0)
        

        self.button.clicked.connect(self.set_terminate_flag)
        self.thread.finished.connect(self.finish)

        
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.xy_label)
        self.layout.addWidget(self.chart_widget)
        self.layout.addWidget(self.img_widget)

        

        # self.img_widget.mousePressEvent = self.on_click
        self.proxy = pg.SignalProxy(self.img_widget.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)

        self.curve = self.chart_widget.plot(pen=pg.mkPen('white', width=3))
        self.img = pg.ImageItem(self.data.T)
        self.img_widget.addItem(self.img)
        if self.show_zero:
            self.zero_ref_line = pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen((255, 0, 0)))
            self.chart_widget.addItem(self.zero_ref_line)

        self.visible_crosshair_pen = pg.mkPen(color=(255,0,0,127), width=1) 
        self.invisible_crosshair_pen = pg.mkPen(color=(0, 0, 0, 0), width=1) 
        self.v_line = pg.InfiniteLine(pos=(self.line_width/2,self.scan_num/2),
                                      angle=90, pen=self.visible_crosshair_pen)
        self.h_line = pg.InfiniteLine(pos=(self.line_width/2,self.scan_num/2),
                                      angle=0, pen=self.visible_crosshair_pen)
        self.img_widget.addItem(self.v_line, ignoreBounds=True)
        self.img_widget.addItem(self.h_line, ignoreBounds=True)

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


    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._is_mouse_pressed = True
            self._mouse_start_pos = event.globalPos()
            self._window_start_pos = self.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_mouse_pressed:
            mouse_delta = event.globalPos() - self._mouse_start_pos
            self.move(self._window_start_pos + mouse_delta)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._is_mouse_pressed = False
    
    def closeEvent(self, event):
        # Terminate the scan safely
        # The user can either click the Terminate button, or click the X button to safety terminate
        self.set_terminate_flag()
        if self.thread.is_finished:

            # print('\n\n\n')
            # print(str(datetime.now()) + ' Will close the window')
            # print('\n\n\n')
            
            self.controller.close_all_windows()
            super().closeEvent(event)
        # Allow the base class to handle the close event
        else:
            event.ignore()
        

    def set_terminate_flag(self):
        self.thread.is_terminated = True
        self.button.clicked.connect(self.controller.close_all_windows)
        # self.close()

    def ui_format(self):

        screen_size = QApplication.primaryScreen().availableGeometry()

        # Calculate 90% of the screen height
        self.img_max_height = int(screen_size.height() * 0.65)

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
        self.img_height = min(self.img_max_height, (self.window_width-x_axis_offset) * self.scan_num/self.line_width)
        self.img_widget.setFixedSize(self.window_width, self.img_height)
        

        


    
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

        # self.mouse_move_is_inside_plot_region = True

        if x_label < 0 or x_label > self.line_width - 1 or y_label < 0 or y_label > self.scan_num - 1:
            # self.mouse_move_is_inside_plot_region = False
            
            self.controller.hide_all_crosshair()
            return


        x_label = max(0, min(x_label, self.line_width - 1))
        y_label = max(0, min(y_label, self.scan_num - 1))

        x_pos = self.position_parameters.x_coordinates[y_label, x_label]
        y_pos = self.position_parameters.y_coordinates[y_label, x_label]

        
     
        # # Update the textbox with the coordinates
        # current_val = self.data[self.scan_num - 1 - y_label, x_label]
        # self.xy_label.setText(f"X, Y position = {x_pos:.1f} µm, {y_pos:.1f} µm, data = {current_val:.2e}")

        self.controller.update_displayed_data(x_label, y_label, x_pos, y_pos)
        

    def updateROI(self):

        roi_pos = (self.roi.pos().x(), self.roi.pos().y())
        roi_size = (self.roi.size().x(), self.roi.size().y())
        self.roi_x_range = (int(roi_pos[0]), int(roi_pos[0]) + int(roi_size[0]))
        self.roi_y_range = (int(roi_pos[1]), int(roi_pos[1]) + int(roi_size[1]))

        self.rescale_color()

    def update_plot(self, data_pack):
        
        self.count, new_data = data_pack
        #self.progress_bar.setValue(self.count)
        #self.progress_bar.setFormat(self.title + f" scanning line " + f"{self.count}/{self.scan_num},"  + f' {self.remaining_time} s remaining')
        self.button.setText(f"Scanning line " + f"{self.count + 1}/{self.scan_num},"  + f' {self.remaining_time} s remaining')
        self.executed_porntion = (self.count+1)/self.scan_num


        self.button.setStyleSheet("""
            QPushButton {
                
                background: qlineargradient(""" + 
                f"""x1: {self.executed_porntion-1E-8}, y1: 0, x2: {self.executed_porntion}, y2: 0, """ + """
                                                    stop: 0 green, 
                                                    stop: 1 rgb(0, 0, 0));
                border: 0px solid black;  /* Black border */
                color: white;  /* White text color */
           
                padding: 5px;  /* Padding inside the button */
            }
            QPushButton:hover {
                 background: qlineargradient(""" + 
                f"""x1: {self.executed_porntion-1E-8}, y1: 0, x2: {self.executed_porntion}, y2: 0, """ + """
                                                    stop: 0 darkgreen, 
                                                    stop: 1 rgb(0, 0, 0));
            }
        """)
                
                

        self.data[self.count] = new_data[self.channel_id]
        
        elapse_time = time.time() - self.time
        if self.count >= 1:
            self.remaining_time = int(elapse_time / self.count * (self.scan_num - self.count))

        self.curve.setData(self.data[self.count])
        self.img.setImage(self.data.T)
        self.rescale_color()
        

        chart_data_max = np.max(self.data[self.count])
        chart_data_min = np.min(self.data[self.count])

        if self.show_zero and chart_data_max < 0:
            self.invisible_ref_line = pg.InfiniteLine(pos=-chart_data_max * 0.1, angle=0, pen=pg.mkPen((0,0,0,0)))
            self.chart_widget.addItem(self.invisible_ref_line)
        if self.show_zero and chart_data_min > 0:
            self.invisible_ref_line = pg.InfiniteLine(pos=-chart_data_min * 0.1, angle=0, pen=pg.mkPen((0,0,0,0)))
            self.chart_widget.addItem(self.invisible_ref_line)

        if self.count == self.scan_num - 1:
            self.pixmap = self.grab()

    def rescale_color(self):
        data = self.data.T[self.roi_x_range[0]:self.roi_x_range[1], self.roi_y_range[0]:self.roi_y_range[1]]
        plot_max_val = np.max(data)
        plot_min_val = np.min(data)
        self.img.setLevels((plot_min_val, plot_max_val))

    def finish(self):
        # When the thread finishes, change the button's text and color

        self.info_label.setText(self.title + '\nClick the button to close immediately')
    
        self.timer_for_count_down = QTimer()
        self.timer_for_count_down.timeout.connect(self.update_countdown_before_close)
        self.timer_for_count_down.start(1000)
        self.auto_close_remaining_time = max(0, self.auto_close_time_in_s)

    def update_countdown_before_close(self):
   
        if self.auto_close_remaining_time >= 0:
            self.button.setText(f"Scan finished, auto close in {int(self.auto_close_remaining_time)} s.")
            self.auto_close_remaining_time -= 1
        else:
            if self.timer_for_count_down.isActive():
                self.timer_for_count_down.stop()
            self.button.setText("Scan finished, the app will close now.")
            self.close()

    

if __name__ == "__main__":
    pass