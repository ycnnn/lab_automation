import numpy as np

class Scan_parameters:
    def __init__(self,
                 input_mapping,
                 frequency,
                 channel_num,
                 DAQ_name='Dev2'):
       
        self.frequency = frequency
        self.channel_num = channel_num
        self.input_mapping = [DAQ_name + '/' +  channel_name for channel_name in input_mapping]
