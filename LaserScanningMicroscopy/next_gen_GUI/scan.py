import numpy as np
import multiprocessing as mp
import sys
######################################################################
# Custom dependencies
from mp import Data_fetcher, Data_receiver
from position_params import Position_parameters
from scan_params import Scan_parameters
######################################################################



if __name__ == '__main__':

    position_parameters = Position_parameters(
                                            x_size=30,
                                            y_size=30,
                                            x_pixels=300,
                                            y_pixels=450,
                                            x_origin=0,
                                            y_origin=0)
    
    scan_parameters = Scan_parameters(frequency=20, 
                                      channel_num=3, 
                                      input_mapping=['ai0', 'ai1','ai4'])

    mp.freeze_support()
    out_pipe, in_pipe = mp.Pipe(duplex=True)
    data_fetcher = Data_fetcher(position_parameters=position_parameters,
                                scan_parameters=scan_parameters, 
                                pipe=out_pipe)
    data_receiver = Data_receiver(position_parameters=position_parameters,
                                  scan_parameters=scan_parameters, 
                                  pipe=in_pipe)
    data_fetcher.start()
    data_receiver.start()
    data_fetcher.join()
    data_receiver.join()

   