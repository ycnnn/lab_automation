import numpy as np
import json

class Scan_parameters:
    def __init__(self,
                 input_mapping=['ai0','ai1','ai2'],
                 frequency=1,
                 retrace_frequency=None,
                 additional_channel_num=0,
                #  channel_num=None,
                 DAQ_name='Dev2',
                 return_to_zero=False):
       
        self.frequency = frequency
        self.retrace_frequency = self.frequency if not retrace_frequency else retrace_frequency
        self.channel_num = len(input_mapping) + additional_channel_num
        self.input_mapping = input_mapping
        self.DAQ_name = DAQ_name
        self.return_to_zero = return_to_zero
        self.save_params()

    def save_params(self):
        self.dict = dict()
        self.dict['frequencies'] = [self.frequency, self.retrace_frequency]
        self.dict['channel_num'] = self.channel_num
        self.dict['input_mapping'] = self.input_mapping
        self.dict['return_to_zero_after_scan'] = self.return_to_zero
 
        self.record = json.dumps(self.dict)
        
