import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 

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




if __name__ == '__main__':
   
    
    try:
        scan_id = sys.argv[1]
    except:
        scan_id = 'imaging'
    
    
    display_parameters = Display_parameters(scan_id=scan_id)

    position_parameters = Position_parameters(
                                            x_size=32,
                                            y_size=32,
                                            x_pixels=80,
                                            y_pixels=80,

                                            x_center=52.2,
                                            y_center=54.7,
                                            z_center=10,
                                            angle=20)
  
    
    scan_parameters = Scan_parameters(point_time_constant=0.01,
                                      return_to_zero=False)

    instruments = []


    daq = inst_driver.DAQ(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    input_mapping=['ai0'],
                    )
    instruments.append(daq)

    laser = inst_driver.LaserDiode(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    **{'current':0.026}
                    )
    instruments.append(laser)



    
    LSM_plot(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters,
             instruments=instruments,
             simulate=False)
    
    
