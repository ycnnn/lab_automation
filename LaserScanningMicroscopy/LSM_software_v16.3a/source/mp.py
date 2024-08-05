import multiprocessing as mp
from PySide6.QtWidgets import QApplication
import sys
import numpy as np
from contextlib import ExitStack
import json
######################################################################
# Custom dependencies
from source.app import QPlot
from source.data_acquisition import Data_acquisitor
from source.daq_driver import reset_daq
import source.inst_driver as inst_driver
######################################################################

class Data_fetcher(mp.Process):
    def __init__(self, 
                 position_parameters,
                 scan_parameters,
                 display_parameters,
                 pipe) -> None:
        mp.Process.__init__(self)
        self.position_parameters = position_parameters
        self.scan_parameters = scan_parameters
        self.line_width = self.position_parameters.x_pixels
        self.scan_num = 2 * self.position_parameters.y_pixels
        self.display_parameters = display_parameters
        self.pipe = pipe
        self.acquisitor = Data_acquisitor(self.position_parameters,
                                          self.scan_parameters)
        

    def run(self):
        ########################################################################
        # Initialize the system position
        reset_daq(self.scan_parameters, destination=self.position_parameters.center_output)



        self.acquisitor.move_origin(initialize=True)
        ########################################################################

        system_instruments = []
        for instrument in self.scan_parameters.instruments:

            print('Initializing instrument: ', instrument.instrument_type)

            instr = inst_driver.configurate_instrument(instrument=instrument,
                                              scan_parameters=self.scan_parameters,
                                              position_parameters=self.position_parameters,
                                              **instrument.kwargs)
            system_instruments.append(instr)

        instrument_manager = [instrument.initialize_instrument for instrument in system_instruments]
        scan_manager = [instrument.scan for instrument in system_instruments]

        with ExitStack() as stack:
            _ = [stack.enter_context(instr()) for instr in instrument_manager]
            
            for scan_index in range(self.scan_num):
                auxiliary_scan_info = {'scan_index': scan_index}
                with ExitStack() as stack:
                    _ = [stack.enter_context(instr_scan(**auxiliary_scan_info)) for instr_scan in scan_manager]
    
                    if scan_index % 2 == 0:
                        data = self.acquisitor.run(scan_index)
                    else:
                        data = self.acquisitor.run(scan_index, retrace=True)
        
                instr_data = np.vstack([resource.data for resource in system_instruments])
                
                # print('Instruments data shape', instr_data.shape)
                
                data = np.vstack((data, instr_data))
                # print('Combined data shape', data.shape)

                self.pipe.send(data)
                status = self.pipe.recv()
                if not status:
                    raise Warning('Possible data loss: Sender not received confirmation from receiver')

     
        self.acquisitor.move_origin(initialize=False)

        ########################################################################
        # [resource.data for resource in system_instruments]
        self.system_instrument_params = {}
        for instr_index, instrument in enumerate(self.scan_parameters.instruments):
            self.system_instrument_params[instrument.instrument_type] = system_instruments[instr_index].instrument_params
            
        
        if self.scan_parameters.return_to_zero:
            reset_daq(self.scan_parameters)
        self.save_instrument_params()
        ########################################################################
    def save_instrument_params(self):
        instr_params_path = self.display_parameters.save_destination + 'parameters/instr_params.json'
        with open(instr_params_path, 'w') as file:
            json.dump(self.system_instrument_params, file, indent=4)



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
        # self.app = QApplication(sys.argv)
        # self.window = QPlot(line_width=self.line_width, scan_num=self.scan_num, channel_num=self.scan_parameters.channel_num)
        # self.window.show()
        self.app = QPlot(line_width=self.line_width, 
                         scan_num=self.scan_num, 
                         channel_num=self.scan_parameters.channel_num,
                         text_bar_height=self.display_parameters.text_bar_height,
                         window_width_min=self.display_parameters.window_width_min,
                         window_width_max=self.display_parameters.window_width_max,
                         show_zero_level=self.display_parameters.show_zero_level,
                         font_size=self.display_parameters.font_size,
                         axis_label_ticks_distance=self.display_parameters.axis_label_ticks_distance)
        #####################################################################

        for scan_index in range(self.scan_num):
            fetch_data = self.pipe.recv()
            # print('\n\n\n')
            # print(fetch_data.shape)
            # print('\n\n\n')
            if scan_index % 2 == 0:
                # Trace
                self.app.update(fetch_data)
            else:
                # Retrace
                self.app.retrace_update(fetch_data)
            
            # print(f'Scan_index {scan_index} data: Receiver received data')
            
            self.pipe.send(True)
            # print(f'Scan_index {scan_index} data: Receiver sent out confirmation')
            counter += 1
            if counter >= self.scan_num:
                break

        if self.display_parameters.save_data:
            self.app.save_results(
                filepath=self.display_parameters.save_destination)

