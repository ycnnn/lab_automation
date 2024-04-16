import numpy as np
import multiprocessing as mp
import time 
import warnings
from PySide6.QtWidgets import QApplication
import sys
######################################################################
# Custom dependencies
from ng_app import QPlot
######################################################################

class Data_acquision(mp.Process):
    def __init__(self, line_width, scan_num, pipe, mode='DAQ') -> None:
        mp.Process.__init__(self)
        self.line_width = line_width
        self.scan_num = scan_num
        self.pipe = pipe
        self.mode = mode
    def run(self):
        for scan_index in range(self.scan_num):
            data = np.random.normal(size=(3, self.line_width))
            self.pipe.send(data)
            print(f'Scan_index {scan_index} data: Sender sent out the data')
            status = self.pipe.recv()
            if not status:
                raise Warning('Possible data loss: Sender not received confirmation from receiver')
            else:
                print(f'Scan_index {scan_index} data: Senter received confirmation\n')

class Data_receiver(mp.Process):
    def __init__(self,line_width, scan_num, pipe) -> None:
        mp.Process.__init__(self)
        self.line_width = line_width
        self.scan_num = scan_num
        self.pipe = pipe
    def run(self):
        counter = 0
        for scan_index in range(self.scan_num):
            data = self.pipe.recv()
            print(f'Scan_index {scan_index} data: Receiver received data')
            self.pipe.send(True)
            print(f'Scan_index {scan_index} data: Receiver sent out confirmation')
            counter += 1
            if counter >= self.scan_num:
                break


if __name__ == '__main__':
    mp.freeze_support()
    out_pipe, in_pipe = mp.Pipe(duplex=True)
    data_acquision = Data_acquision(line_width=256, scan_num=100, pipe=out_pipe)
    data_receiver = Data_receiver(line_width=256, scan_num=100, pipe=in_pipe)
    data_acquision.start()
    data_receiver.start()
    data_acquision.join()
    data_receiver.join()

   