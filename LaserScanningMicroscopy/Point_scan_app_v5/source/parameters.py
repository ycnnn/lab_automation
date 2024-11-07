import os
import numpy as np
from pathlib import Path

class Position_parameters:
    def __init__(self, center=(0,0,0), angle=0, length=0, steps=10, return_to_zero=False):

        self.return_to_zero = return_to_zero
        self.xy_conversion = 0.10
        self.z_conversion = 0.20

        self.angle_radian = angle / 180.0 * np.pi
        self.x_center, self.y_center, self.z_center = center
        self.x_unrot = np.linspace(-length/2, length/2, num=steps)
        self.y_unrot = np.zeros(shape=steps) * self.y_center
        self.z = np.ones(shape=steps) * self.z_center
        self.x_rot = np.cos(self.angle_radian) * self.x_unrot + np.sin(self.angle_radian) * self.y_unrot + self.x_center
        self.y_rot = - np.sin(self.angle_radian) * self.x_unrot + np.cos(self.angle_radian) * self.y_unrot + self.y_center

        self.center_output = np.array([self.x_center * self.xy_conversion, 
                              self.y_center * self.xy_conversion, 
                              self.z_center * self.z_conversion])
        self.DAQ_output_data = np.array([self.x_rot * self.xy_conversion, 
                           self.y_rot * self.xy_conversion, 
                           self.z * self.z_conversion])

class Scan_paramters:
    def __init__(self, 
                 scan_id='scan_',
                 steps=500, 
                 save_destination=None,
                 position_parameters=None):
        self.steps = steps
        self.scan_id = scan_id
        self.save_destination = save_destination
        # self.save_destination = save_destination if save_destination else os.path.dirname(os.path.realpath(__file__))
        self.create_path()
        self.position_parameters = position_parameters if position_parameters else Position_parameters(steps=self.steps)

    def create_path(self):
        full_path = os.path.realpath(__file__)
        path = str(Path(os.path.dirname(full_path)).parents[0].absolute()) + '/results/' + self.scan_id + '/'
    
        self.save_destination = path if not self.save_destination else self.save_destination
       
        # The following code save the data.
        # In case there is already a filder that hav the same name as the save desitnation,
        # The code will rename the old folder by adding a suffix of "_backup".
        # In cases there is alreay a backup folder, the code will add a number to suffix to identify each backup.
        # For example: if "test" alreay exist, the code will try to move the old data to "text_backup_1"; if "text_backup_1" is also there, the code will try change the identifier to "text_backup_2", "text_backup_3", "text_backup_4" etc.
        # In short, the code NEVER overwrites nor DELETES your data!

        if os.path.exists(self.save_destination):
            # If the directory does not exist, create it

            uniq = 1
            backup_path = path[:-1] + '_backup_' + str(uniq) + '/'
            while os.path.exists(backup_path):
                uniq += 1
                backup_path = path[:-1] + '_backup_' + str(uniq) + '/'
        
            os.rename(self.save_destination, backup_path)

        os.makedirs(self.save_destination)
        
def main():
    pass



if __name__ == "__main__":
    main()
