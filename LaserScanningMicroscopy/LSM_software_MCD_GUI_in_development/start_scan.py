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
from source.plot_process import LSM_plot
import source.inst_driver as inst_driver



def scan_start():
  
    display_parameters = Display_parameters(scan_id='test', window_width=400)

    position_parameters = Position_parameters(
                                            x_size=50,
                                            y_size=50,
                                            x_pixels=200,
                                            y_pixels=200,
                                            z_center=0,
                                            # A positiove angle rotates the image clockwise. Negative angle for counterclockwise.
                                            angle=45)
  
    scan_parameters = Scan_parameters(point_time_constant=0.0006,
                                    #   retrace_point_time_constant=0.02,
                                      return_to_zero=False)

    instruments = []

    daq = inst_driver.DAQ_simulated(
                    name='My_DAQ',
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    input_mapping=['ai0', 'ai1', 'ai3'],
                    )
    instruments.append(daq)

    scan = LSM_plot(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters,
             instruments=instruments,
             auto_close_time_in_s=10,
             simulate=True,
             show_zero=True)

    




if __name__ == "__main__":
    
    scan_start()
    '''
    # You can call start the scan multiple times. This feature is helpful if you want to automate multiple scans one by one. Like the following:
    scan_start()
    '''
    




 
