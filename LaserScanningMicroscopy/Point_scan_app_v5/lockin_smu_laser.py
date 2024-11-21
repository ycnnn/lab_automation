# import sys, os
# from PySide6 import QtWidgets
# import time, random
# from contextlib import ExitStack
# from pathlib import Path
# from source.app import LSMLivePlot
# from source.log_config import setup_logging
import numpy as np
import source.instruments as inst_driver
from source.parameters import Scan_paramters, Position_parameters
from source.scan_process import LSM_single_scan

def main():

    scan_id = input('Enter scanid:\n')
    instruments = []
    steps = 80
    # position_parameters = Position_parameters(steps=steps)
    scan_parameters = Scan_paramters(steps=steps, scan_id=scan_id)
    

    # daq = inst_driver.DAQ_simulated(
    #                 scan_parameters=scan_parameters,
    #                 input_mapping=['ai0','ai1'],
    #                 )
    # instruments.append(daq)

    smu_G = inst_driver.SMU(scan_parameters=scan_parameters,
                 address="USB0::0x05E6::0x2450::04096331::INSTR",
                 mode='Force_V_Sense_V',
                 **{'Source':[-40,40]})
    instruments.append(smu_G)

    # smu_D = inst_driver.SMU(scan_parameters=scan_parameters,
    #              address="USB0::0x05E6::0x2450::04096333::INSTR",
    #              mode='Force_V_Sense_I',
    #              **{'Source':[-1,1]})
    # instruments.append(smu_D)





    lockin = inst_driver.Lockin(scan_parameters=scan_parameters,
                                **{
                                    'time_constant_level':11, 
                                    'volt_input_range':3, 
                                    'signal_sensitivity':7,
                    })
    instruments.append(lockin)

    laser = inst_driver.LaserDiode(scan_parameters=scan_parameters)
    instruments.append(laser)


    LSM_single_scan(
             scan_parameters=scan_parameters,
             instruments=instruments,
             simulate=False)
   

if __name__ == "__main__":
    main()
