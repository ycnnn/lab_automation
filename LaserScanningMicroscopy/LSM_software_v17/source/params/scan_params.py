import numpy as np
import json


class Scan_parameters:
    def __init__(self,
                 point_time_constant=0.001,
                 retrace_point_time_constant=None,
                 DAQ_name='Dev2',
                 return_to_zero=False):
       
        self.point_time_constant = point_time_constant
        self.retrace_point_time_constant = self.point_time_constant if not retrace_point_time_constant else retrace_point_time_constant
        # additional_channel_num = instrument.additional_channel_num if instrument else 0
        # self.channel_num = len(input_mapping) + additional_channel_num
        
        self.DAQ_name = DAQ_name
        self.return_to_zero = return_to_zero
        # self.instrument = instrument

        # self.save_params()


    def save_params(self, filepath):
        self.dict = dict()
        self.dict['point_time_constant'] = [self.point_time_constant, self.retrace_point_time_constant]
        self.dict['return_to_zero_after_scan'] = self.return_to_zero
 
        # self.record = json.dumps(self.dict)
        scan_params_filepath = filepath + 'parameters/scan_params.json'

        with open(scan_params_filepath, 'w') as file:
            json.dump(self.dict, file, indent=4)
        
