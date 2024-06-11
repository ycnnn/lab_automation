import numpy as np

class Scan_parameters:
    def __init__(self,
                 input_mapping,
                 frequency,
                 channel_num,
                 DAQ_name='Dev2'):
       
        self.frequency = frequency
        self.channel_num = channel_num
        self.input_mapping = input_mapping
        self.DAQ_name = DAQ_name
