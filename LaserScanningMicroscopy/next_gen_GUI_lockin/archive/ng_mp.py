import numpy as np
import multiprocessing as mp
import time 
import warnings
from PySide6.QtWidgets import QApplication
import sys
######################################################################
# Custom dependencies
from ng_app import QPlot
from ng_data_acquisition import Data_acquisitor
######################################################################

class Data_fetcher(mp.Process):
    def __init__(self, line_width, scan_num, pipe, mode='DAQ') -> None:
        mp.Process.__init__(self)
        self.line_width = line_width
        self.scan_num = scan_num
        self.pipe = pipe
        self.mode = mode
        self.acquisitor = Data_acquisitor(line_width=self.line_width, 
                                          scan_num=self.scan_num, 
                                          channel_num=3)

    def run(self):
        for scan_index in range(self.scan_num):

            data = self.acquisitor.run()
            self.pipe.send(data)
            # print(f'Scan_index {scan_index} data: Sender sent out the data')
            status = self.pipe.recv()
            if not status:
                raise Warning('Possible data loss: Sender not received confirmation from receiver')
            else:
                # print(f'Scan_index {scan_index} data: Senter received confirmation\n')
                pass

class Data_receiver(mp.Process):
    def __init__(self,line_width, scan_num, pipe) -> None:
        mp.Process.__init__(self)
        self.line_width = line_width
        self.scan_num = scan_num
        self.pipe = pipe
       


    def run(self):
        counter = 0

        #####################################################################
        # Initilize plots
        self.app = QApplication(sys.argv)
        self.window = QPlot(line_width=self.line_width, scan_num=self.scan_num, channel_num=3)
        self.window.show()
        #####################################################################

        for scan_index in range(self.scan_num):
           
            
            fetch_data = self.pipe.recv()
            # print(f'Scan_index {scan_index} data: Receiver received data')
            self.window.update(fetch_data)
            self.pipe.send(True)
            # print(f'Scan_index {scan_index} data: Receiver sent out confirmation')
            counter += 1
            if counter >= self.scan_num:
                break

