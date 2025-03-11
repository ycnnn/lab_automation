import sys
import os, platform
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLabel
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
from source.subwindow import SubWindow
import source.inst_driver as inst_driver



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

class AppController:
    def __init__(self, channel_num, save_destination, gui_start_scan_button=None):
        self.windows = []
        self.channel_num = channel_num
        self.save_destination = save_destination
        self.gui_start_scan_button = gui_start_scan_button

    def add_window(self, window):
        self.windows.append(window)

    def update_displayed_data(self, x_label, y_label, x_pos, y_pos):
     
        inside_plot_region = True
        
     
        for window in self.windows:
            current_val = window.data[window.scan_num - 1 - y_label, x_label]
            window.xy_label.setText(f"X, Y = {x_pos:.1f} µm, {y_pos:.1f} µm\nData = {current_val:.2e}")

            window.v_line.setPen(window.visible_crosshair_pen)
            window.h_line.setPen(window.visible_crosshair_pen)
            window.v_line.setPos((x_label,window.scan_num - 1 - y_label))
            window.h_line.setPos((x_label,window.scan_num - 1 - y_label))


    def hide_all_crosshair(self):

        for window in self.windows:
            window.h_line.setPen(window.invisible_crosshair_pen)
            window.v_line.setPen(window.invisible_crosshair_pen)

    def grab_screenshot(self):
        for channel_id in range(self.channel_num):
            pixmap = self.windows[channel_id].grab()
            # self.windows[channel_id].pixmap.save(self.display_parameters.save_destination + self.windows[channel_id].title + '.png')
            pixmap.save(self.save_destination + self.windows[channel_id].title + '.png')

    def close_all_windows(self):
        
        self.grab_screenshot()
        
        for window in self.windows:
            window.close()
        if not self.gui_start_scan_button:
            self.gui_start_scan_button.setEnabled(True) 

class LSM_plot:

    def __init__(self, 
                 display_parameters, 
                 position_parameters, 
                 scan_parameters, 
                 instruments, 
                 auto_close_time_in_s=360,
                 show_zero=True,
                 simulate=False,
                 app=None,
                 gui_start_scan_button=None):

        self.data_thread = LSM_scan(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters,
             instruments=instruments,
             simulate=simulate)
        self.channel_names = self.data_thread.channel_names 
        self.display_parameters = display_parameters

        scan_num, line_width = (position_parameters.y_pixels,position_parameters.x_pixels)
        self.channel_num = self.data_thread.channel_num
        self.master_app_exists = False
        if app:
            self.app = app
            self.master_app_exists = True
        else:
            if not QApplication.instance():
                self.app = QApplication([])
            else:
                self.app = QApplication.instance()
        screen_width = self.app.primaryScreen().size().width()
        screen_height = self.app.primaryScreen().size().height()

        self.gui_start_scan_button = gui_start_scan_button
        self.controller = AppController(channel_num=self.channel_num,
                                        save_destination=self.display_parameters.save_destination,
                                        gui_start_scan_button=self.gui_start_scan_button)
        
       
        default_font_size = screen_height / 70
        font_family = load_font('font/SourceCodePro-Medium.ttf')
        if font_family:
            global_font = QFont(font_family)
            if self.display_parameters.font_size:
                global_font.setPointSize(self.display_parameters.font_size)
            else:
                global_font.setPointSize(default_font_size)
            self.app.setFont(global_font)

        self.windows = []

        
        
        
        if self.display_parameters.window_width:
            window_width = self.display_parameters.window_width
        else:
            window_width = screen_width/4
        window_displacement = min(window_width, (screen_width-window_width)/self.channel_num)
        for channel_id in range(self.channel_num):
            window = SubWindow(channel_id=channel_id, 
                               controller=self.controller,
                            title=self.channel_names[channel_id],
                            scan_num=scan_num, line_width=line_width,
                            position_parameters=position_parameters,
                            thread=self.data_thread,
                            show_zero=show_zero,
                            auto_close_time_in_s=auto_close_time_in_s,
                            window_width=window_width)
            window.move(window_displacement * channel_id,0)
            self.data_thread.data_ready.connect(window.update_plot)
            self.windows.append(window)
        
        self.run()

    def run(self):
        # Start the data thread
        self.data_thread.start()

        # Show both windows
        for channel_id in range(self.channel_num):
            self.windows[channel_id].show()
        if not self.master_app_exists:
            self.app.exec()



if __name__ == "__main__":
    pass
