import numpy as np
import multiprocessing as mp
# import multiprocess as mp
# import sys
######################################################################
# Custom dependencies
from mp import Data_fetcher, Data_receiver
# from params.position_params import Position_parameters
# from params.scan_params import Scan_parameters
# from params.display_params import Display_parameters
######################################################################

def lsm_scan(position_parameters, 
             scan_parameters, 
             display_parameters):
    mp.freeze_support()
    out_pipe, in_pipe = mp.Pipe(duplex=True)
    data_fetcher = Data_fetcher(position_parameters=position_parameters,
                                scan_parameters=scan_parameters, 
                                display_parameters=display_parameters,
                                pipe=out_pipe)
    data_receiver = Data_receiver(position_parameters=position_parameters,
                                  scan_parameters=scan_parameters, 
                                  display_parameters=display_parameters,
                                  pipe=in_pipe)
    data_fetcher.start()
    data_receiver.start()
    data_fetcher.join()
    data_receiver.join()

    scan_parameters.save_params(filepath=(display_parameters.save_destination + display_parameters.scan_id))
    position_parameters.save_params(filepath=(display_parameters.save_destination + display_parameters.scan_id))
    


