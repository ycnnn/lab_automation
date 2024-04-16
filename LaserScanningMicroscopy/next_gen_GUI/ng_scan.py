import numpy as np
import multiprocessing as mp
######################################################################
# Custom dependencies
from ng_mp import Data_fetcher, Data_receiver
######################################################################



if __name__ == '__main__':


    line_width=512
    scan_num=512


    mp.freeze_support()
    out_pipe, in_pipe = mp.Pipe(duplex=True)
    data_fetcher = Data_fetcher(line_width=line_width, scan_num=scan_num, pipe=out_pipe)
    data_receiver = Data_receiver(line_width=line_width, scan_num=scan_num, pipe=in_pipe)
    data_fetcher.start()
    data_receiver.start()
    data_fetcher.join()
    data_receiver.join()

   