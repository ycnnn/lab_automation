# import shutil
# import os
import sys
import numpy as np
######################################################################
# Custom dependencies
# from mp import Data_fetcher, Data_receiver
from source.params.position_params import Position_parameters
from source.params.scan_params import Scan_parameters
from source.params.display_params import Display_parameters
from source.scan_process import LSM_scan
import source.inst_driver as inst_driver
# from source.inst_driver import External_instrument, EmptyInstrument
######################################################################



if __name__ == '__main__':
   
    
    try:
        scan_id = sys.argv[1]
    except:
        scan_id = 'scan'
    
    
    display_parameters = Display_parameters(scan_id=scan_id)

    position_parameters = Position_parameters(
                                            x_size=0,
                                            y_size=0,
                                            x_center=0,
                                            y_center=0,
                                            x_pixels=100,
                                            y_pixels=10,
                                            z_center=0,
                                            angle=-35)
  
    
    scan_parameters = Scan_parameters(point_time_constant=0.01,
                                    #   retrace_point_time_constant=0.01,
                                      return_to_zero=True)

    instruments = []

    daq = inst_driver.DAQ(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    input_mapping=['ai0'],
                    )
    instruments.append(daq)

    # smu = inst_driver.SMU(
    #                 position_parameters=position_parameters,
    #                 scan_parameters=scan_parameters,
    #                 **{'voltage':1},
    #                 )
    # instruments.append(smu)

    # laser = inst_driver.LaserDiode(
    #                 position_parameters=position_parameters,
    #                 scan_parameters=scan_parameters,
    #                 **{'current':0.005},
    #                 )
    # instruments.append(laser)


    # lockin_prop = {
    #     'time_constant_level':9,
    #     'volt_input_range':2,
    #     'signal_sensitivity':6,
    #     'ref_frequency':[1000,100000],
    #     'sine_amplitude':0.1,}
    
    # lockin = inst_driver.Lockin(
    #                 position_parameters=position_parameters,
    #                 scan_parameters=scan_parameters,
    #                 **lockin_prop,
    #                 )
    # instruments.append(lockin)




    # sim_instr_params = {'param1': 22, 'param2':[0,0], 'param3':0}
    # sim_instr = inst_driver.SimulatedInstrument(
    #                 address='',
    #                 position_parameters=position_parameters,
                
    #                 # name='Sim1',
    #                 **sim_instr_params
    #                 )
    # instruments.append(sim_instr)

    rotator = inst_driver.RotationStage(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    **{'angle':150},
                    )
    instruments.append(rotator)

    



    
    LSM_scan(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters,
             instruments=instruments)
    
    
