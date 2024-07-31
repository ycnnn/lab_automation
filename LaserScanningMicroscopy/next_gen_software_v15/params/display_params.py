import numpy as np
import os
import shutil
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
                 window_width_min=300, 
                 window_width_max=500,
                 save_data=True):
        
        if len(scan_id) == 0:
            scan_id = 'temp_scan'
        
        self.scan_id = 'temp_scan' if not scan_id else scan_id
        
        full_path = os.path.realpath(__file__)
        path = str(Path(os.path.dirname(full_path)).parent.absolute()) + '/results/' + self.scan_id + '/'
        self.save_destination = path if not save_destination else save_destination

        # The following code save the data.
        # In case there is already a filder that hav the same name as the save desitnation,
        # The code will rename the old folder by adding a suffix of "_backup".
        # In cases there is alreay a backup folder, the code will add a number to suffix to identify each backup.
        # For example: if "test" alreay exist, the code will try to move the old data to "text_backup_1"; if "text_backup_1" is also there, the code will try change the identifier to "text_backup_2", "text_backup_3", "text_backup_4" etc.
        # In short, the code NEVER overwrites nor DELETES your data!

        if not os.path.exists(self.save_destination):
            # If the directory does not exist, create it
            os.makedirs(self.save_destination)

        else:
            uniq = 1
            backup_path = path[:-1] + '_backup_' + str(uniq) + '/'
            while os.path.exists(backup_path):
                uniq += 1
                backup_path = path[:-1] + '_backup_' + str(uniq) + '/'
            shutil.copytree(self.save_destination, backup_path)
            shutil.rmtree(self.save_destination)
            os.makedirs(self.save_destination)
        

        os.makedirs(self.save_destination + 'data/')
        os.makedirs(self.save_destination + 'data_text/')
        os.makedirs(self.save_destination + 'parameters/')

        self.colormap = colormap
        self.channel_min = channel_min
        self.channel_max = channel_max
        self.window_width = window_width
        self.window_height = window_height
        self.text_bar_height = text_bar_height
        self.window_width_min = window_width_min
        self.window_width_max = window_width_max
        self.darkmode = darkmode
        self.save_data = save_data


       
        
