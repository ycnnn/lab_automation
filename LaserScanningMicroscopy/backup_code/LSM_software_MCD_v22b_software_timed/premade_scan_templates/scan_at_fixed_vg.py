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
   
    vg = 0
    vd = 0

    try:
        scan_id = sys.argv[1]
    except:
        scan_id = f'VJ_Vg_{vg}_vd_{vd}'
    
    # Fixed gate bias Vg, in volt
    

    # Load calibration data for rotating the waveplates in the system.
    # The data will have multiple rows, each row is data for a certain polarization angle of the light shining on the sample.
    # for each row, there will be 4 values, which are rotating angles for:
    # the angle of halfwaveplate(HWP) before the balance detector, the polarization angle of the light shining on the sample, 
    # the angle of quarterwaveplate(QWP) in the upstream of lightpath, and
    # the angle of halfwaveplate(HWP) in the upstream of lightpath.
    # The HWP and QWP in the upstream of the light is used to cancel all birefingent behavior of the optics in the system,
    # such that the light shining on the sample is linearly polarized.
    # All angles in degrees

    
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
  
    
    scan_parameters = Scan_parameters(point_time_constant=0.035,
                                      retrace_point_time_constant=0.005,
                                      return_to_zero=False,
                                      additional_info=f'')

    instruments = []

    daq = inst_driver.DAQ(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    input_mapping=['ai0'],
                    )
    instruments.append(daq)

    smu_gate = inst_driver.SMU(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    **{'voltage':vg},
                    )
    instruments.append(smu_gate)

    # smu_drain = inst_driver.SMU(
    #                 address="USB0::0x05E6::0x2450::04096333::INSTR",
    #                 position_parameters=position_parameters,
    #                 scan_parameters=scan_parameters,
    #                 **{'voltage':vd},
    #                 )
    # instruments.append(smu_drain)

    laser = inst_driver.LaserDiode(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    **{'current':0.026},
                    )
    instruments.append(laser)


    lockin_prop = {
        'time_constant_level':9,
        'volt_input_range':2,
        'signal_sensitivity':7,}
    
    lockin = inst_driver.Lockin(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    **lockin_prop,
                    )
    instruments.append(lockin)


    



    
    LSM_plot(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters,
             instruments=instruments)
    
    
