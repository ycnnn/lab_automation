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


class LSM_plot:

    def __init__(self, 
                 display_parameters, 
                 position_parameters, 
                 scan_parameters, 
                 instruments, 
                 simulate=True):

        self.data_thread = LSM_scan(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters,
             instruments=instruments,
             simulate=simulate)
        self.channel_names = self.data_thread.channel_names 
        self.display_parameters = display_parameters

        scan_num, line_width = (position_parameters.y_pixels,position_parameters.x_pixels)
        self.channel_num = self.data_thread.channel_num

        self.app = QApplication([])
        font_family = load_font('font/SourceCodePro-Medium.ttf')
        if font_family:
            global_font = QFont(font_family)
            global_font.setPixelSize(12)
            self.app.setFont(global_font)

        self.windows = []
        for channel_id in range(self.channel_num):
            window = SubWindow(channel_id=channel_id, 
                            title=self.channel_names[channel_id],
                            scan_num=scan_num, line_width=line_width)
            self.data_thread.data_ready.connect(window.update_plot)
            self.windows.append(window)

        
        self.run()

    def run(self):
        # Start the data thread
        self.data_thread.start()

        # Show both windows
        for channel_id in range(self.channel_num):
            self.windows[channel_id].show()
    
        self.app.exec()

        for channel_id in range(self.channel_num):
            pixmap = self.windows[channel_id].grab()
            # self.windows[channel_id].pixmap.save(self.display_parameters.save_destination + self.windows[channel_id].title + '.png')
            pixmap.save(self.display_parameters.save_destination + self.windows[channel_id].title + '.png')


if __name__ == "__main__":
    pass
