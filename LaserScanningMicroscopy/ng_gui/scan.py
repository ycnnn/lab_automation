import numpy as np
import multiprocessing as mp
import sys
######################################################################
# Custom dependencies
from mp import Data_fetcher, Data_receiver
from params.position_params import Position_parameters
from params.scan_params import Scan_parameters
from params.display_params import Display_parameters
######################################################################



if __name__ == '__main__':

    position_parameters = Position_parameters(
                                            x_size=15,
                                            y_size=15,
                                            x_pixels=256,
                                            y_pixels=256,
                                            x_origin=10,
                                            y_origin=10,
                                            z_height=19)
    
    scan_parameters = Scan_parameters(frequency=10, 
                                      channel_num=3, 
                                      input_mapping=["ai0","ai1","ai3"])
    
    display_parameters = Display_parameters(
                 scan_id='01',
                 save_destination=None,
                 colormap=None,
                 channel_min=None,
                 channel_max=None,
                 window_width=None,
                 window_height=None,
                 darkmode=True,
                 save_data=True)

    mp.freeze_support()
    out_pipe, in_pipe = mp.Pipe(duplex=True)
    data_fetcher = Data_fetcher(position_parameters=position_parameters,
                                scan_parameters=scan_parameters, 
                                pipe=out_pipe)
    data_receiver = Data_receiver(position_parameters=position_parameters,
                                  scan_parameters=scan_parameters, 
                                  display_parameters=display_parameters,
                                  pipe=in_pipe)
    data_fetcher.start()
    data_receiver.start()
    data_fetcher.join()
    data_receiver.join()
    

   