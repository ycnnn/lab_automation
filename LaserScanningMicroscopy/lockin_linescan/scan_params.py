from write_control import position_parameters, sweep_xy, sweep_x_theta
import os
import json
import numpy as np

class params:
    def __init__(self,
                 pixels=100,
                 frequency = 1100,
                 scale = 0.60,
                 window_width=1495,
                 window_height = 800,
                 colormap='bwr',
                 auto_scale=True,
                 ch1_v_min=-9.9,
                 ch1_v_max=9.9,
                 ch2_v_min=-9.9,
                 ch2_v_max=9.9,
                 ch3_v_min=-9.9,
                 ch3_v_max=9.9,
                 dark_mode=False,
                 x_center=65,
                 y_center=80,
                 x_size=20,
                 y_size=20,
                 angle=-90,
                 conversion_factor=0.0049,
                 xy_scan=True,
                 scan_id='_scan',
                 target_folder=None,
                 save_during_scan=False,
                 theta_start=None,
                 theta_end=None,
                 input_mapping=["Dev1/ai0", "Dev1/ai4", "Dev1/ai20"]):
        # Note: vmin, vmax used to set caling will only work if auto_scale==False!
        if pixels <= 1:
            pixels = 2
        self.pixels = pixels
        self.frequency = frequency
        self.scale = scale
        self.window_width = window_width
        self.window_height = window_height
        self.colormap = colormap
        self.conversion_factor = conversion_factor
        self.auto_scale = auto_scale
        self.x_center = x_center
        self.y_center = y_center
        self.x_size = x_size
        self.y_size = y_size
        self.angle = angle
        self.val_range_1 = (ch1_v_min, ch1_v_max)
        self.val_range_2 = (ch2_v_min, ch2_v_max)
        self.val_range_3 = (ch3_v_min, ch3_v_max)
        self.dark_mode = dark_mode
        self.theta_val = None
        self.theta_steps = self.pixels
        self.theta_start = theta_start
        self.theta_end = theta_end
        self.input_mapping = input_mapping
        
        # Determines xy scan or (x, theta) scan
        self.xy_scan=xy_scan
        # If not XY scan (that is, X-Theta scan), freeze scan size along y
        if not self.xy_scan:
            self.y_size = 0.0001
            if theta_start and theta_end:
                self.theta_val = np.linspace(self.theta_start,self.theta_end,num=self.pixels)
            else:
                print('X-Theta scan parameters error')
  
        

        self.scan_id = scan_id
        if not target_folder:
            self.target_folder = os.path.abspath('') + '\\results\\'
        if not os.path.isdir(self.target_folder):
            os.mkdir(self.target_folder)
        self.save_destination = self.target_folder + scan_id


        self.position = position_parameters(
            x_center=x_center,
            y_center=y_center,
            x_size=x_size,
            y_size=y_size,
            angle=angle,
            conversion_factor=conversion_factor,
            pixels=pixels)

        self.daq_ao_channel_num, self.x_coordinates, self.y_coordinates = sweep_xy(self.position)
        
    
    def save_params(self):
        params_dict = {'pixels':self.pixels,
                 'frequency' : self.frequency,
                 'scale' : self.scale,
                 'window_width':self.window_width,
                 'window_height' : self.window_height,
                 'colormap':self.colormap,
                 'auto_scale':self.auto_scale,
                 'ch1_v_min':self.val_range_1[0],
                 'ch1_v_max':self.val_range_1[1],
                 'ch2_v_min':self.val_range_2[0],
                 'ch2_v_max':self.val_range_2[1],
                 'ch3_v_min':self.val_range_3[0],
                 'ch3_v_max':self.val_range_3[1],
                 'dark_mode':self.dark_mode,
                 'x_center':self.x_center,
                 'y_center':self.y_center,
                 'x_size':self.x_size,
                 'y_size':self.y_size,
                 'angle':self.angle,
                 'conversion_factor':self.conversion_factor,
                 'xy_scan':self.xy_scan,
                 'scan_id':self.scan_id,
                 'target_folder':self.target_folder,
                 'theta_start' : self.theta_start,
                 'theta_end': self.theta_end,
                 'theta_steps' : self.theta_steps,
                 'input_channels':self.input_mapping}
        if os.path.isfile(self.save_destination + '.json'):
            os.remove(self.save_destination + '.json')
        with open(self.save_destination + '.json','w') as f:
            json.dump(params_dict,f)

