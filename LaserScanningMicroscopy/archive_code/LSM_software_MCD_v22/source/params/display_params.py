import numpy as np
import os
import shutil
from pathlib import Path

class Display_parameters:
    def __init__(self,
                 scan_id=None,
                 save_destination=None,
                 window_width=None,
                 font_size=None,
                 axis_label_ticks_distance=12,
               ):
        
        if len(scan_id) == 0:
            scan_id = 'temp_scan'
        
        self.scan_id = 'temp_scan' if not scan_id else scan_id
    
        
        full_path = os.path.realpath(__file__)
        path = str(Path(os.path.dirname(full_path)).parents[1].absolute()) + '/results/' + self.scan_id + '/'
    
        self.save_destination = path if not save_destination else save_destination
        self.axis_label_ticks_distance = axis_label_ticks_distance
        self.font_size = font_size
       

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
            # shutil.copytree(self.save_destination, backup_path)
            # shutil.rmtree(self.save_destination)
            # os.makedirs(self.save_destination)
            os.rename(self.save_destination, backup_path)
        

        os.makedirs(self.save_destination + 'data/')
        os.makedirs(self.save_destination + 'data_text/')
        os.makedirs(self.save_destination + 'parameters/')

   
        self.window_width = window_width
        self.font_size = font_size





       


       
        
