import numpy as np
import warnings

class Position_parameters:
    def __init__(self,
                 x_size=30,
                 y_size=30,
                 x_pixels=128,
                 y_pixels=128,
                 x_origin=0,
                 y_origin=0,
                 z_origin=0,
                 axis_motion_low_limit=0.0,
                 axis_motion_high_limit=9.50, 
                 conversion_factor=0.1):

        self.x_origin, self.y_origin = (x_origin, y_origin)
        self.x_size, self.y_size = (abs(x_size), abs(y_size))
        self.x_pixels, self.y_pixels = (int(abs(x_pixels)), int(abs(y_pixels)))
        self.x_pixels = max(1, self.x_pixels)
        self.y_pixels = max(1, self.y_pixels)
        self.axis_limits = (axis_motion_low_limit, axis_motion_high_limit)
        self.z_origin = z_origin
        self.conversion_factor = conversion_factor


        self.generate_sweep_coordiantes()
        self.generate_initial_moves()

    def input_check(self, origin, size=0):
        if (origin + size)*self.conversion_factor > self.axis_limits[1] or origin*self.conversion_factor < self.axis_limits[0]:
            return True 
        
    def generate_sweep_coordiantes(self):

        if (self.input_check(self.x_origin, self.x_size) or self.input_check(self.y_origin, self.y_size)):
            warnings.warn('The requested XY motion range is outisde the accpeted limits. For MCL NanoT115 scanner, the minimum input voltage is 0V and the max 10V. The scan will go on, but the scan region will be clipped and image may be distorted.', stacklevel=2)


        self.x_coordinates = np.repeat(
            np.clip(
            self.conversion_factor * np.linspace(self.x_origin,self.x_origin + self.x_size,num=self.x_pixels), 
                a_min=self.axis_limits[0], 
                a_max=self.axis_limits[1]
                ).reshape(1,-1),
        repeats=self.y_pixels, axis=0) 

        self.y_coordinates = np.repeat(
        np.clip(
          self.conversion_factor * np.linspace(self.y_origin,self.y_origin + self.y_size,num=self.y_pixels), 
          a_min=self.axis_limits[0], 
          a_max=self.axis_limits[1]
          ).reshape(1,-1),
        repeats=self.x_pixels, axis=0).T

        ###########################
        # This line flips the x coordinates on even rows, such that the lens travels like a snake
        self.x_coordinates[1::2, :] = self.x_coordinates[1::2, ::-1]

    def generate_initial_moves(self):
        # Initial: (0,0) to (x_origin, y_origin)
        # Final: self.x_coordinates[self.y_pixels-1, self.x_pixels-1], self.x_coordinates[self.y_pixels-1, self.x_pixels-1] to 0,0
        
        self.initial_move = np.array([
            np.linspace(0, self.x_origin, num=self.x_pixels), 
            np.linspace(0, self.y_origin, num=self.x_pixels)]).T
        final_x_location = self.x_coordinates[self.y_pixels-1, self.x_pixels-1]
        final_y_location = self.y_coordinates[self.y_pixels-1, self.x_pixels-1]
        self.final_move = np.array([
            np.linspace(final_x_location, 0, num=self.x_pixels), 
            np.linspace(final_y_location, 0, num=self.x_pixels)]).T
       

    def save_params(self, save_name):
        pass
   


