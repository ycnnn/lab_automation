import numpy as np
import multiprocessing as mp
from contextlib import ExitStack
import json
import os
import base64
# import multiprocess as mp
# import sys
######################################################################
# Custom dependencies
# from source.inst_driver import External_instrument
# from source.app import QPlot
# from source.logger import Logger
# from source.data_acquisition import Data_acquisitor
from source.daq_driver import reset_daq
import source.inst_driver as inst_driver
from source.plot_process import Data_receiver
from source.log_config import setup_logging

class LSM_scan:
    
    def __init__(self,
                  position_parameters, 
                  scan_parameters, 
                  display_parameters,
                  instruments=[]):
        

          
        self.scan_parameters = scan_parameters
        self.position_parameters = position_parameters
        self.display_parameters = display_parameters

        self.instruments = instruments

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
        
        daq_exists = any(
            isinstance(instrument, inst_driver.DAQ) for instrument in self.instruments)
        
        if not daq_exists:
            raise RuntimeError('DAQ not added to instrument list.')

        for instr_index, instr in enumerate(self.instruments):
            if isinstance(instr, inst_driver.DAQ):
                break

        daq = self.instruments[instr_index]
        self.instruments.pop(instr_index)

        daq_exists = any(
            isinstance(instrument, inst_driver.DAQ) for instrument in self.instruments)
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
   
        

        self.start_scan()
        self.save_parameters()
        self.save_data()

       

    def start_scan(self):


        self.logger.info('Scan started.\n\n')

        # mp.freeze_support()
        self.out_pipe, self.in_pipe = mp.Pipe(duplex=True)

        self.data_receiver = Data_receiver(position_parameters=self.position_parameters,
                                    scan_parameters=self.scan_parameters, 
                                    display_parameters=self.display_parameters,
                                    channel_num=self.channel_num,
                                    pipe=self.in_pipe)
        
        self.data_receiver.start()
     
    
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
                        
                    with ExitStack() as scan_stack:
                        _ = [scan_stack.enter_context(
                                instr_scan(**auxiliary_scan_info)
                                ) for instr_scan in scan_manager]
                 
                    instr_data = np.vstack([
                            resource.data for resource in self.instruments
                            ])

                    self.out_pipe.send(instr_data)

                    status = self.out_pipe.recv()
                    if not status:
                        raise Warning('Possible data loss: Sender not received confirmation from receiver')
        
        self.data, self.retrace_data = self.out_pipe.recv()

        self.screenshots = self.out_pipe.recv()

       
        self.data_receiver.join()


        self.logger.info('\n\nScan finished.\n\n')

        
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

            image_base64 = self.screenshots[channel_id]
            # Decode the base64 string into binary data
            image_data = base64.b64decode(image_base64)
            # Save the binary data as a PNG file
            with open(filepath + save_channel_name_list[channel_id] + '.png', "wb") as file:
                file.write(image_data)

            np.save(
                (filepath + f'data/trace_data_' + save_channel_name_list[
                    channel_id]), 
                       self.data[channel_id])
            
            np.save(
                (filepath + f'data/retrace_data_' + save_channel_name_list[
                    channel_id]), 
                       self.data[channel_id])
            
            np.savetxt(
                (filepath + f'data_text/trace_data_' + save_channel_name_list[
                    channel_id] + '.csv'), 
                       self.data[channel_id], 
                       delimiter=',')
            np.savetxt(
                (filepath + f'data_text/retrace_data_' + save_channel_name_list[
                    channel_id] + '.csv'), 
                       self.retrace_data[channel_id], 
                       delimiter=',')


