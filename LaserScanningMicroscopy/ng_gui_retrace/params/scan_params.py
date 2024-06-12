import numpy as np

class Scan_parameters:
    def __init__(self,
                 input_mapping=['ai0','ai1','ai2'],
                 frequency=1,
                 retrace_frequency=1,
                 channel_num=None,
                 DAQ_name='Dev2'):
       
        self.frequency = frequency
        self.retrace_frequency = retrace_frequency
        self.channel_num = len(input_mapping) if not channel_num else channel_num
        self.input_mapping = input_mapping
        self.DAQ_name = DAQ_name
