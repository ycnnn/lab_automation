import numpy as np
import multiprocessing as mp
import time 
import warnings

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
            print(f'Scan_index {scan_index} data: sender sent out the data')
            status = self.pipe.recv()
            if not status:
                raise Warning('Possible data loss: sender not received confirmation from receiver')
            else:
                print(f'Scan_index {scan_index} data: senter received confirmation\n')

class Plot(mp.Process):
    def __init__(self,line_width, scan_num, pipe) -> None:
        mp.Process.__init__(self)
        self.line_width = line_width
        self.scan_num = scan_num
        self.pipe = pipe
    def run(self):
        counter = 0
        for scan_index in range(self.scan_num):
            data = self.pipe.recv()
            print(f'Scan_index {scan_index} data: receiver received data')
            self.pipe.send(True)
            print(f'Scan_index {scan_index} data: receiver sent out confirmation')
            counter += 1
            if counter >= self.scan_num:
                break


if __name__ == '__main__':
    mp.freeze_support()
    out_pipe, in_pipe = mp.Pipe(duplex=True)
    data_acquision = Data_acquision(line_width=256, scan_num=100, pipe=out_pipe)
    plot = Plot(line_width=256, scan_num=100, pipe=in_pipe)
    data_acquision.start()
    plot.start()
    data_acquision.join()
    plot.join()

    # data_acquision = Data_acquision()

    # # start = time.time()
    # recv_pipe, send_pipe = mp.Pipe(duplex=True)

    # sender_process = mp.Process(target=sender, args=(send_pipe,))
    # receiver_process = mp.Process(target=receiver, args=(recv_pipe,))

    # sender_process.start()
    # receiver_process.start()
    # sender_process.join()
    # receiver_process.join()
    # print(10000/(time.time()-start))