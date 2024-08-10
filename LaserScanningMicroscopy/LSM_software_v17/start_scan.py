import shutil
import os
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
                                            y_pixels=99,
                                            z_center=0,
                                            angle=-35)
  
    
    scan_parameters = Scan_parameters(point_time_constant=0.0001,
                                    #   retrace_point_time_constant=0.01,
                                      input_mapping=["ai0"],
                                      return_to_zero=True)

    instruments = []


    


    vir_instr = inst_driver.VirtualInstrument(
                    address='',
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    )
    instruments.append(vir_instr)



    sim_instr_params = {'param1': 22, 'param2':[0,100], 'param3':np.random.random(
        size=(2, position_parameters.y_pixels))}
    sim_instr = inst_driver.SimulatedlInstrument(
                    address='',
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters,
                    **sim_instr_params
                    )
    instruments.append(sim_instr)





    
    LSM_scan(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters,
             instruments=instruments)
    
    
