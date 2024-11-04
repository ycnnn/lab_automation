import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 

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
        scan_id = 'imaging'
    
    
    display_parameters = Display_parameters(scan_id=scan_id)

    position_parameters = Position_parameters(
                                            x_size=50,
                                            y_size=50,
                                            x_pixels=100,
                                            y_pixels=100,
                                            z_center=0,
                                            angle=-35)
  
    
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
                    **{'current':0.065},
                    )
    instruments.append(laser)



    
    LSM_scan(position_parameters=position_parameters,
             scan_parameters=scan_parameters,
             display_parameters=display_parameters,
             instruments=instruments)
    
    
