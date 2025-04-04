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
from source.parameters import Position_parameters
from source.parameters import Scan_paramters
# from source.parameters import Display_parameters
from source.scan_process import LSM_single_scan
import source.instruments as inst_driver




    

if __name__ == "__main__":

    instruments = []
    steps = 10
    position_parameters = Position_parameters(steps=steps)
    scan_parameters = Scan_paramters(steps=steps, position_parameters=position_parameters)
    

    daq = inst_driver.DAQ_simulated(
                    scan_parameters=scan_parameters,
                    input_mapping=['ai0','ai1'],
                    )
    instruments.append(daq)


    LSM_single_scan(
            caller_file_path=os.path.abspath(__file__),
             scan_parameters=scan_parameters,
             instruments=instruments,
             simulate=True)
   



 