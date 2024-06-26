
import multiprocessing as mp

from PySide6.QtWidgets import QApplication
import sys
import pyvisa
import numpy as np

######################################################################
# Custom dependencies
from app import QPlot
from data_acquisition import Data_acquisitor
from daq_driver import reset_daq
######################################################################

class Data_fetcher(mp.Process):
    def __init__(self, 
                 position_parameters,
                 scan_parameters,
                 pipe) -> None:
        mp.Process.__init__(self)
        self.position_parameters = position_parameters
        self.scan_parameters = scan_parameters
        self.line_width = self.position_parameters.x_pixels
        self.scan_num = 2 * self.position_parameters.y_pixels
        self.pipe = pipe
        self.acquisitor = Data_acquisitor(self.position_parameters,
                                          self.scan_parameters)
        

    def run(self):
        ########################################################################
        # Initialize the system position
        reset_daq(self.scan_parameters, destination=self.position_parameters.center_output)



        self.acquisitor.move_origin(initialize=True)

        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################
        rm = pyvisa.ResourceManager()
        instrument = rm.open_resource('USB0::0xB506::0x2000::002765::INSTR')

        instrument.write('*rst')
        instrument.query('*idn?')
        instrument.write('capturelen 256')
        instrument.write('capturecfg xy')
        instrument.write('rtrg posttl')
        ###################################################################################
        ###################################################################################
        ###################################################################################
        ###################################################################################


        ########################################################################
        for scan_index in range(self.scan_num):
            # Note: there are trace and retrace scans, separately
            if scan_index % 2 == 0:
                ###################################################################################
                ###################################################################################
                ###################################################################################
                ###################################################################################
                instrument.write('capturestart one, samp')
                ###################################################################################
                ###################################################################################
                ###################################################################################
                ###################################################################################
                # Trace
                data = self.acquisitor.run(scan_index)

                ###################################################################################
                ###################################################################################
                ###################################################################################
                ###################################################################################
                instrument.write('capturestop')
                buffer_len = int(instrument.query('captureprog?')[:-1])
                inst_data = np.array(instrument.query_binary_values(f'captureget? 0, {buffer_len}')).reshape(-1,2)
                ###################################################################################
                ###################################################################################
                ###################################################################################
                ###################################################################################
            else:
                # Retrace
                data = self.acquisitor.run(scan_index, retrace=True)
            self.pipe.send(data)
            status = self.pipe.recv()
            if not status:
                raise Warning('Possible data loss: Sender not received confirmation from receiver')
        # After last scan finishes: the obj lens should move to the origin again
        ########################################################################\
        # Move the obj lens back to (0,0)
        # self.acquisitor.move_origin(initialize=False)

        
        self.acquisitor.move_origin(initialize=False)
        
        if self.scan_parameters.return_to_zero:
            reset_daq(self.scan_parameters)
        ########################################################################

class Data_receiver(mp.Process):
    def __init__(self,
                 position_parameters,
                 scan_parameters,
                 display_parameters,
                 pipe) -> None:
        mp.Process.__init__(self)
        self.position_parameters = position_parameters
        self.scan_parameters = scan_parameters
        self.display_parameters = display_parameters
        self.line_width = self.position_parameters.x_pixels
        self.scan_num = 2 * self.position_parameters.y_pixels
        self.pipe = pipe
       


    def run(self):
        counter = 0

        #####################################################################
        # Initilize plots
        self.app = QApplication(sys.argv)
        self.window = QPlot(line_width=self.line_width, scan_num=self.scan_num, channel_num=self.scan_parameters.channel_num)
        self.window.show()
        #####################################################################

        for scan_index in range(self.scan_num):
            fetch_data = self.pipe.recv()
            if scan_index % 2 == 0:
                # Trace
                self.window.update(fetch_data)
            else:
                # Retrace
                self.window.retrace_update(fetch_data)
            
            # print(f'Scan_index {scan_index} data: Receiver received data')
            
            self.pipe.send(True)
            # print(f'Scan_index {scan_index} data: Receiver sent out confirmation')
            counter += 1
            if counter >= self.scan_num:
                break

        if self.display_parameters.save_data:
            self.window.save_results(
                filepath=self.display_parameters.save_destination,
                scan_id=self.display_parameters.scan_id)

