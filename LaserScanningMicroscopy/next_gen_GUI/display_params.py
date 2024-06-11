import numpy as np
import os

class Display_parameters:
    def __init__(self,
                 scan_id=None,
                 save_destination=None,
                 colormap=None,
                 channel_min=None,
                 channel_max=None,
                 window_width=None,
                 window_height=None,
                 darkmode=None):
       
        self.frequency = frequency
        self.channel_num = channel_num
        self.input_mapping = [DAQ_name + '/' +  channel_name for channel_name in input_mapping]
