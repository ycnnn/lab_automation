import numpy as np

class Scan_parameters:
    def __init__(self,
                 frequency=2.5,
                 channel_num=3,
                 input_mapping=['ai0', 'ai1', 'ai2'],
                 DAQ_name='Dev2'):
       
        self.frequency = frequency
        self.channel_num = channel_num
        self.input_mapping = [DAQ_name + '/' +  channel_name for channel_name in input_mapping]
