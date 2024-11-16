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

    x_pixels, y_pixels = (100,100)

    position_parameters = Position_parameters(
                                            x_size=20,
                                            y_size=20,
                                            x_pixels=x_pixels,
                                            y_pixels=y_pixels,
                                            z_center=10,
                                            angle=0)
  
    
    scan_parameters = Scan_parameters(point_time_constant=0,
                                    #   retrace_point_time_constant=0.02,
                                      return_to_zero=False)

    instruments = []

    daq = inst_driver.DAQ(
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    input_mapping=['ai0', 'ai1'],
                    )
    instruments.append(daq)

    # daq = inst_driver.DAQ_simulated(
    #                 position_parameters=position_parameters,
    #                 scan_parameters=scan_parameters,
    #                 input_mapping=['ai0'],
    #                 )
    # instruments.append(daq)

    # smu = inst_driver.SMU(
    #                 position_parameters=position_parameters,
    #                 scan_parameters=scan_parameters,
    #                 **{'source':np.linspace(0,1,num=240).reshape(2,12,10)},
    #                 verbose=True
    #                 )
    # instruments.append(smu)

    # laser = inst_driver.LaserDiode(
    #                 position_parameters=position_parameters,
    #                 scan_parameters=scan_parameters,
    #                 **{'current':0.005 +   0.005 * (np.arange(2*y_pixels*x_pixels)%2).reshape(2,y_pixels,x_pixels)},
    #                 )
    # instruments.append(laser)


    # lockin_prop = {
    #     'time_constant_level':12,
    #     'volt_input_range':(np.arange(2*y_pixels*x_pixels)%2).reshape(2,y_pixels,x_pixels),
    #     'signal_sensitivity':12,}
    
    # lockin = inst_driver.Lockin(
    #                 position_parameters=position_parameters,
    #                 scan_parameters=scan_parameters,
    #                 **lockin_prop,
    #                 )
    # instruments.append(lockin)




    # sim_instr_params = {'param1': np.random.normal(size=(2,12,10)), 'param2':0, 'param3':3}
    # sim_instr = inst_driver.SimulatedInstrument(
    #                 address='',
    #                 position_parameters=position_parameters,
                
    #                 # name='Sim1',
    #                 **sim_instr_params
    #                 )
    # instruments.append(sim_instr)

    # correction_hwp = inst_driver.RotationStage(
    #                 position_parameters=position_parameters,
    #                 scan_parameters=scan_parameters,
    #                 name='HWP_for_correction',
    #                 address=55422054,
    #                 **{'angle':0},
    #                 )
    # instruments.append(correction_hwp)

    # correction_qwp = inst_driver.RotationStage(
    #                 position_parameters=position_parameters,
    #                 scan_parameters=scan_parameters,
    #                 name='QWP_for_correction',
    #                 address=55425654,
    #                 **{'angle':0},
    #                 )
    # instruments.append(correction_qwp)

    # hwp_before_bd = inst_driver.RotationStage(
    #                 position_parameters=position_parameters,
    #                 scan_parameters=scan_parameters,
    #                 name='HWP_for_zeroing_BD_output',
    #                 address=55425494,
    #                 **{'angle':0},
    #                 )
    # instruments.append(hwp_before_bd)

    



    
    LSM_scan(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters,
             instruments=instruments,
             simulate=False)
    
    
