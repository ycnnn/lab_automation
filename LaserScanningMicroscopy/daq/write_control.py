import numpy as np

class position_parameters:
    def __init__(self,
                 x_center,
                 y_center,
                 x_size,
                 y_size,
                 angle,
                 conversion_factor,
                 pixels):

        
        self.x_center, self.y_center = (x_center, y_center)
        self.x_size, self.y_size = (x_size, y_size)
        self.angle = angle*np.pi/180.00
        self.conversion_factor = conversion_factor
        self.pixels = pixels

def sweep_xy(position_parameters):
    daq_ao_channel_num = 2
    angle = position_parameters.angle
    pixels = position_parameters.pixels
    x_offset, y_offset = (position_parameters.x_center, position_parameters.y_center)
    x_size, y_size = (position_parameters.x_size, position_parameters.y_size)

    x_coordinates_original = np.repeat(
        np.linspace(-x_size/2,x_size/2,num=pixels).reshape(1,-1),
        repeats=pixels, axis=0)
    y_coordinates_original = np.repeat(
      np.linspace(-y_size/2,y_size/2,num=pixels).reshape(1,-1),
      repeats=pixels, axis=0).T
    x_coordinates = (  np.cos(angle) * x_coordinates_original 
                     - np.sin(angle) * y_coordinates_original
                     + x_offset)
    y_coordinates = (  np.sin(angle) * x_coordinates_original 
                     + np.cos(angle) * y_coordinates_original
                     + y_offset)
    
    return (daq_ao_channel_num, 
            position_parameters.conversion_factor * np.flip(x_coordinates,axis=0), 
            position_parameters.conversion_factor * np.flip(y_coordinates,axis=0))

def sweep_x_theta():
    daq_ao_channel_num = 1
    pass

