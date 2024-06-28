import numpy as np
import warnings
import json

class Position_parameters:
    def __init__(self,
                 x_size=30,
                 y_size=30,
                 x_pixels=128,
                 y_pixels=None,
                 x_center=50,
                 y_center=50,
                 z_center=0,
                 angle=0,
                 axis_motion_low_limit=0.0,
                 axis_motion_high_limit=9.50, 
                 conversion_factor=0.1,
                 z_conversion_factor=0.2):
        
        self.conversion_factor = conversion_factor
        self.z_conversion_factor = z_conversion_factor
        self.x_center, self.y_center = (x_center, y_center)
        self.x_size, self.y_size = (abs(x_size), abs(y_size))
        y_pixels = x_pixels if not y_pixels else y_pixels
        self.x_pixels, self.y_pixels = (int(abs(x_pixels)), int(abs(y_pixels)))
        self.x_pixels = max(1, self.x_pixels)
        self.y_pixels = max(1, self.y_pixels)
        self.axis_limits = (axis_motion_low_limit, axis_motion_high_limit)
        self.z_center = z_center

        self.x_center_output = self.x_center * self.conversion_factor
        self.y_center_output = self.y_center * self.conversion_factor
        self.z_center_output = self.z_center * self.z_conversion_factor
        
        self.center_output = np.array([
            self.x_center_output,
            self.y_center_output,
            self.z_center_output,
            0
        ])

        self.angle = angle * np.pi / 180
        


        self.generate_sweep_coordiantes()
        self.move_center()
        # self.save_params()

    def input_check(self, center, conversion_factor, size=0):
        if (center + size/2)*conversion_factor > self.axis_limits[1] or (center - size/2)*conversion_factor < self.axis_limits[0]:
            return True 
        
    def create_reverse_scan(self, input_data):

        data = np.repeat(input_data[:,:,np.newaxis],axis=2,repeats=2).reshape(self.y_pixels,-1)
        height, length = data.shape
        new_data = np.zeros((height*2,length))
        new_data[::2,:] = data
        new_data[1::2,:] = np.flip(data, axis=1)

        return new_data
                
    def generate_sweep_coordiantes(self):

        if (self.input_check(self.x_center, self.conversion_factor, self.x_size) 
            or self.input_check(self.y_center, self.conversion_factor, self.y_size)
            or self.input_check(self.z_center, self.z_conversion_factor, 0)):
            warnings.warn('\nThe requested XYZ motion range is outside the accpeted limits. \nFor MCL NanoT115 scanner, the minimum input voltage is 0V and the max 10V. \nThe scan will go on, but the scan region will be clipped and image may be distorted.', stacklevel=2)


        self.x_coordinates_unrotated = np.repeat(
            np.linspace(-self.x_size/2,self.x_size/2,num=self.x_pixels).reshape(1,-1),
            repeats=self.y_pixels, axis=0) 
        # print('Self x_coordinates unrot shape=')
        # print(self.x_coordinates_unrotated.shape)
        
        self.y_coordinates_unrotated = np.repeat(
            np.linspace(-self.y_size/2,self.y_size/2,num=self.y_pixels).reshape(1,-1),
            repeats=self.x_pixels, axis=0).T
        # print('Self y_coordinates unrot shape=')
        # print(self.y_coordinates_unrotated.shape)
        
        #########################################################################
        # Rotation
        self.x_coordinates = (  
            np.cos(self.angle) * self.x_coordinates_unrotated 
            - np.sin(self.angle) * self.y_coordinates_unrotated
            + self.x_center)
        
        self.y_coordinates = (  
            np.sin(self.angle) * self.x_coordinates_unrotated 
            + np.cos(self.angle) * self.y_coordinates_unrotated
            + self.y_center)
       
        
        self.z_coordinates = self.z_center * np.ones(self.x_coordinates.shape)

        #########################################################################
        # Converting to DAQ output

        self.x_output = np.clip(
            self.conversion_factor * self.x_coordinates, 
                a_min=self.axis_limits[0], 
                a_max=self.axis_limits[1]
                )
        self.y_output = np.clip(
            self.conversion_factor * self.y_coordinates, 
                a_min=self.axis_limits[0], 
                a_max=self.axis_limits[1]
                )
        
        self.z_output = np.clip(
            self.z_conversion_factor * self.z_coordinates, 
                a_min=self.axis_limits[0], 
                a_max=self.axis_limits[1]
                )
        self.ttl = 3.50 * np.ones(self.x_coordinates.shape)
        
        #########################################################################
        # Creating reverse scan output data
        
        self.x_output = self.create_reverse_scan(self.x_output)
        self.y_output = self.create_reverse_scan(self.y_output)
        self.z_output = self.create_reverse_scan(self.z_output)
        self.ttl = self.create_reverse_scan(self.ttl)
        ttl_height, ttl_length = self.ttl.shape
        self.ttl[:,::2] = np.zeros((ttl_height, int(ttl_length/2)))

        #########################################################################
        # Optional, make the scanned image look like the real image
        # self.x_output = np.flip(self.x_output, axis=0)
        # self.y_output = np.flip(self.y_output, axis=0)
        # self.z_output = np.flip(self.z_output, axis=0)

        # self.x_output = np.flip(self.x_output, axis=1)
        # self.y_output = np.flip(self.y_output, axis=1)
        # self.z_output = np.flip(self.z_output, axis=1)
        #########################################################################
   



        self.DAQ_output_data = np.array([self.x_output,
                                         self.y_output,
                                         self.z_output,
                                         self.ttl])
        self.DAQ_output_data = np.flip(self.DAQ_output_data, axis=(1,2))
    

    def move_center(self):
        # Move from current location to the center

        self.initial_move = np.linspace(
            np.array([self.x_center_output, 
                    self.y_center_output,
                    self.z_center_output,
                    0]),
            np.array([self.DAQ_output_data[0,0,0], 
                    self.DAQ_output_data[1,0,0],
                    self.DAQ_output_data[2,0,0],
                    0]),
            num=self.x_pixels
        )

        self.final_move = np.linspace(
            np.array([self.DAQ_output_data[0,-1,-1], 
                    self.DAQ_output_data[1,-1,-1],
                    self.DAQ_output_data[2,-1,-1],
                    0]),
            np.array([self.x_center_output, 
                    self.y_center_output,
                    self.z_center_output,
                    0]),
            num=self.x_pixels
        )

        
       

    def save_params(self, filepath):
        self.dict = dict()
        self.dict['centers'] = [self.x_center, self.y_center, self.z_center]
        self.dict['angle'] = self.angle
        self.dict['scan_size'] = [self.x_size, self.y_size]
        self.dict['pixels'] = [self.x_pixels, self.y_pixels]
        self.dict['conversion_factor'] = [self.conversion_factor, self.z_conversion_factor]
        self.dict['output_limit'] = self.axis_limits
        # self.record = json.dumps(self.dict)

        position_params_filepath = filepath + 'position_params.json'

        with open(position_params_filepath, 'w') as file:
            json.dump(self.dict, file, indent=4)
        
   


