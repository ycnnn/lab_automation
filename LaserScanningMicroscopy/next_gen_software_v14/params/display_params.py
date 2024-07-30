import numpy as np
import os
from pathlib import Path

class Display_parameters:
    def __init__(self,
                 scan_id=None,
                 save_destination=None,
                 colormap=None,
                 channel_min=None,
                 channel_max=None,
                 window_width=None,
                 window_height=None,
                 darkmode=True,
                 text_bar_height=20,
                 save_data=True):
        
        if len(scan_id) == 0:
            scan_id = 'temp_scan'
        
        self.scan_id = 'temp_scan' if not scan_id else scan_id
        
        full_path = os.path.realpath(__file__)
        path = str(Path(os.path.dirname(full_path)).parent.absolute()) + '/results/' + self.scan_id + '/'
        self.save_destination = path if not save_destination else save_destination

        if not os.path.exists(self.save_destination):
            # If the directory does not exist, create it
            os.makedirs(self.save_destination)

        self.colormap = colormap
        self.channel_min = channel_min
        self.channel_max = channel_max
        self.window_width = window_width
        self.window_height = window_height
        self.text_bar_height = text_bar_height
        self.darkmode = darkmode
        self.save_data = save_data
       
        
