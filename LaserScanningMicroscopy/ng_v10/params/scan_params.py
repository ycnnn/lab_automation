import numpy as np
import json


class Scan_parameters:
    def __init__(self,
                 input_mapping=['ai0','ai1','ai2'],
                 frequency=1,
                 retrace_frequency=None,
                #  instrument=None,
                 DAQ_name='Dev2',
                 return_to_zero=False):
       
        self.frequency = frequency
        self.retrace_frequency = self.frequency if not retrace_frequency else retrace_frequency
        # additional_channel_num = instrument.additional_channel_num if instrument else 0
        # self.channel_num = len(input_mapping) + additional_channel_num
        self.channel_num = len(input_mapping) 
        self.input_mapping = input_mapping
        self.DAQ_name = DAQ_name
        self.return_to_zero = return_to_zero
        # self.instrument = instrument
        self.instruments = []
        self.save_params()

    def add_instrument(self, instrument):
        self.instruments.append(instrument)
        self.channel_num += instrument.additional_channel_num
        pass

    def save_params(self, filepath):
        self.dict = dict()
        self.dict['frequencies'] = [self.frequency, self.retrace_frequency]
        self.dict['channel_num'] = self.channel_num
        self.dict['input_mapping'] = self.input_mapping
        self.dict['return_to_zero_after_scan'] = self.return_to_zero
        self.dict['channel_num'] = self.channel_num
        self.dict['instrument_list'] = [instr.instrument_type for instr in self.instruments]
 
        # self.record = json.dumps(self.dict)
        scan_params_filepath = filepath + '_scan_params.json'

        with open(scan_params_filepath, 'w') as file:
            json.dump(self.dict, file, indent=4)
        
