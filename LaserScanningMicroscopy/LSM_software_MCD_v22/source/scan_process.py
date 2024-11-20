import numpy as np
import multiprocessing as mp
from contextlib import ExitStack
import json
import os
import base64
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QGuiApplication, QFontDatabase, QFont, QColor, QPixmap, QPen
from PySide6.QtCore import Qt, QByteArray, QBuffer, QLoggingCategory, QThread, Signal
######################################################################

import source.inst_driver as inst_driver
from source.log_config import setup_logging

class LSM_scan(QThread):

    data_ready = Signal(list)
    finished = Signal()

    def __init__(self,
                  position_parameters, 
                  scan_parameters, 
                  display_parameters,
                  instruments=[],
                  simulate=False):
        super().__init__()
        self.scan_parameters = scan_parameters
        self.position_parameters = position_parameters
        self.display_parameters = display_parameters

        self.instruments = instruments
        self.simulate = simulate

        self.is_terminated = False


        # Mandatory code. There MUST be at least one external instrument present dring the scan.
        empty_instr = inst_driver.EmptyInstrument(
            address='',
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters
                    )
        self.instruments.append(empty_instr)

        laser_exists = any(
            isinstance(instrument, inst_driver.LaserDiode) for instrument in self.instruments)
        if laser_exists:
            for instr_index, instr in enumerate(self.instruments):
                if isinstance(instr, inst_driver.LaserDiode):
                    break
            laser = self.instruments[instr_index]
            self.instruments.pop(instr_index)
            self.instruments.append(laser)

        DAQ_type = inst_driver.DAQ if not self.simulate else inst_driver.DAQ_simulated
        
        daq_exists = any(
            isinstance(instrument, DAQ_type) for instrument in self.instruments)

        
        if not daq_exists:
            raise RuntimeError('DAQ not added to instrument list.')

        for instr_index, instr in enumerate(self.instruments):
            if isinstance(instr, DAQ_type):
                break

        daq = self.instruments[instr_index]
        self.instruments.pop(instr_index)

        daq_exists = any(
            isinstance(instrument, DAQ_type) for instrument in self.instruments)
        if daq_exists:
            raise RuntimeError('DAQ has been added twice. Check instruments settings.')
        
        self.instruments.append(daq)

        # for instr_index, instr in enumerate(self.instruments):
        #     print(type(instr))

        self.line_width = self.position_parameters.x_pixels
        self.total_scan_num = 2 * self.position_parameters.y_pixels

        self.channel_num = 0

        for instrument in self.instruments:
            self.channel_num += instrument.channel_num

        # Set up the logging process
        self.logger = setup_logging(self.display_parameters.save_destination)
   
        self.channel_names = []
        for instrument in self.instruments:
            for channel_name in instrument.channel_name_list:
                self.channel_names.append(channel_name)

        self.data = np.zeros((2,self.channel_num, self.position_parameters.y_pixels, self.position_parameters.x_pixels))
   
    
    def run(self):


        self.logger.info('Scan started.')

        ########################################################
        '''
        Initialize the plot
        '''
     
    
        instrument_manager = [
                instrument.initialize_and_quit for instrument in self.instruments]
        
        scan_manager = [instrument.scan for instrument in self.instruments]

        auxiliary_init_info = {'logger': self.logger}
        with ExitStack() as init_stack:
            _ = [init_stack.enter_context(
                    instr(**auxiliary_init_info)
                    ) for instr in instrument_manager]

            for total_scan_index in range(self.total_scan_num):
                    auxiliary_scan_info = {'total_scan_index': total_scan_index}
                    
                    if self.is_terminated:
                        terminated_message = 'The user has terminated the scan. All isntruments will be exited safely.'
                        self.logger.info(terminated_message)
                        raise RuntimeError(terminated_message)
                    
                    with ExitStack() as scan_stack:
                        _ = [scan_stack.enter_context(
                                instr_scan(**auxiliary_scan_info)
                                ) for instr_scan in scan_manager]
              
                    instr_data = np.vstack([
                            resource.data for resource in self.instruments
                            ])
               
                
                    if total_scan_index % 2 == 0:
                        scan_index = int(total_scan_index / 2)
                        self.data_ready.emit([scan_index, instr_data])
                        self.data[0, :, scan_index, :] = instr_data
                    else:
                        scan_index = int((total_scan_index - 1) / 2)
                        self.data[1, :, scan_index, :] = instr_data
                    
        self.finished.emit()

        self.logger.info('Scan finished.')
        self.save_data()
        self.save_parameters()
        
    def save_parameters(self):
        ######################################################################
        # Save all scanning-related parameters

        self.scan_parameters.save_params(self.display_parameters.save_destination)
        self.position_parameters.save_params(self.display_parameters.save_destination)
        
        instr_params_save_filepath = self.display_parameters.save_destination + 'parameters/instr_params.json'

        instr_params = {}
        for instr in self.instruments:
            instr_params[instr.name] = instr.params_config_save

        with open(instr_params_save_filepath, 'w') as file:
            json.dump(instr_params, file, indent=8)
    
    def save_data(self):

        filepath = self.display_parameters.save_destination
        
        # for channel_id in range(self.channel_num):
        #     img = self.windows[channel_id].grab(self.windows[channel_id].rect())
        #     img.save(filepath + f'screenshot_channel_{channel_id}.' + fileformat, fileformat)

        save_channel_name_list = []

        for instrument in self.instruments:
            for channel_name in instrument.channel_name_list:
                save_channel_name_list.append(channel_name)
        


        
        for channel_id in range(self.channel_num):

            # image_base64 = self.screenshots[channel_id]
            # # Decode the base64 string into binary data
            # image_data = base64.b64decode(image_base64)
            # # Save the binary data as a PNG file
            # with open(filepath + save_channel_name_list[channel_id] + '.png', "wb") as file:
            #     file.write(image_data)

            np.save(
                (filepath + f'data/trace_data_' + save_channel_name_list[
                    channel_id]), 
                       self.data[0, channel_id])
            
            np.save(
                (filepath + f'data/retrace_data_' + save_channel_name_list[
                    channel_id]), 
                       self.data[1, channel_id])
            
            np.savetxt(
                (filepath + f'data_text/trace_data_' + save_channel_name_list[
                    channel_id] + '.csv'), 
                       self.data[0, channel_id], 
                       delimiter=',')
            np.savetxt(
                (filepath + f'data_text/retrace_data_' + save_channel_name_list[
                    channel_id] + '.csv'), 
                       self.data[1, channel_id], 
                       delimiter=',')


