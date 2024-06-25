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
                 z_height=0,
                 axis_motion_low_limit=0.0,
                 axis_motion_high_limit=9.50, 
                 conversion_factor=0.1,
                 z_conversion_factor=0.2):
        
        self.conversion_factor = conversion_factor
        self.z_conversion_factor = z_conversion_factor
        self.x_origin, self.y_origin = (x_origin, y_origin)
        self.x_size, self.y_size = (abs(x_size), abs(y_size))
        self.x_pixels, self.y_pixels = (int(abs(x_pixels)), int(abs(y_pixels)))
        self.x_pixels = max(1, self.x_pixels)
        self.y_pixels = max(1, self.y_pixels)
        self.axis_limits = (axis_motion_low_limit, axis_motion_high_limit)
        self.z_height = z_height
        self.z_output = self.z_height * self.z_conversion_factor
        


        self.generate_sweep_coordiantes()
        self.generate_initial_moves()

    def input_check(self, origin, conversion_factor, size=0):
        if (origin + size)*conversion_factor > self.axis_limits[1] or origin*conversion_factor < self.axis_limits[0]:
            return True 
        
    def create_reverse_scan(self, input_data):

        data = np.repeat(input_data[:,:,np.newaxis],axis=2,repeats=2).reshape(self.y_pixels,-1)
        height, length = data.shape
        new_data = np.zeros((height*2,length))
        new_data[::2,:] = data
        new_data[1::2,:] = np.flip(data, axis=1)

        return new_data
                
    def generate_sweep_coordiantes(self):

        if (self.input_check(self.x_origin, self.conversion_factor, self.x_size) 
            or self.input_check(self.y_origin, self.conversion_factor, self.y_size)
            or self.input_check(self.z_height, self.z_conversion_factor, 0)):
            warnings.warn('The requested XYZ motion range is outisde the accpeted limits. For MCL NanoT115 scanner, the minimum input voltage is 0V and the max 10V. The scan will go on, but the scan region will be clipped and image may be distorted.', stacklevel=2)


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

        self.z_coordinates = self.z_output * np.ones(self.x_coordinates.shape)
        self.ttl = 3.50 * np.ones(self.x_coordinates.shape)

        self.x_coordinates = self.create_reverse_scan(self.x_coordinates)
        self.y_coordinates = self.create_reverse_scan(self.y_coordinates)
        self.z_coordinates = self.create_reverse_scan(self.z_coordinates)
        self.ttl = self.create_reverse_scan(self.ttl)
        ttl_height, ttl_length = self.ttl.shape
        self.ttl[:,::2] = np.zeros((ttl_height, int(ttl_length/2)))

        # ###########################
        # # This line flips the x coordinates on even rows, such that the lens travels like a snake
        # self.x_coordinates[1::2, :] = self.x_coordinates[1::2, ::-1]

        # ###########################
        # # Prepare for lock-in interface scan
        # # What happens there: we repeat every pixel two times, so the overall data supplied to DAQ has shape of (3, self.y_pixels, 2*self.x_pixles)
        # # First dim: which data: 0 = TTL signal, 1 = X_coordinates, 2 = Y_coordinates
        # self.x_coordinates = np.repeat(self.x_coordinates[:,:,np.newaxis],axis=2,repeats=2).reshape(self.y_pixels,-1)
        # self.y_coordinates = np.repeat(self.y_coordinates[:,:,np.newaxis],axis=2,repeats=2).reshape(self.y_pixels,-1)
        # self.z_coordinates = self.z_height * self.z_conversion_factor * np.ones(self.x_coordinates.shape)
        # self.ttl = 3.5 * np.repeat(
        #     np.ravel(np.column_stack((
        #                         np.ones(self.x_pixels),
        #                         np.zeros(self.x_pixels)
        #                         )))[np.newaxis,:],
        #                         axis=0,repeats=self.y_pixels
        #                         )
        self.DAQ_output_data = np.array([self.x_coordinates,
                                         self.y_coordinates,
                                         self.z_coordinates,
                                         self.ttl])
        # print(self.ttl.shape)
        # print(self.x_coordinates.shape)

    def generate_initial_moves(self):
        # Initial: (0,0) to (x_origin, y_origin)
        # Final: self.x_coordinates[self.y_pixels-1, self.x_pixels-1], self.x_coordinates[self.y_pixels-1, self.x_pixels-1] to 0,0
        
        # self.initial_move = np.array([
        #     np.linspace(0, self.x_origin * self.conversion_factor, num=self.x_pixels), 
        #     np.linspace(0, self.y_origin * self.conversion_factor, num=self.x_pixels),
        #     np.linspace(0, self.z_height * self.z_conversion_factor, num=self.x_pixels),
        #     np.zeros(self.x_pixels)]).T
        
        self.initial_move = np.linspace(
            np.zeros(4),
            np.array([self.x_origin * self.conversion_factor, 
                      self.y_origin * self.conversion_factor,
                      self.z_height * self.z_conversion_factor,
                      0]),
            num=self.x_pixels
        )
        

        # final_x_location = self.x_coordinates[self.y_pixels-1, self.x_pixels-1]
        # final_y_location = self.y_coordinates[self.y_pixels-1, self.x_pixels-1]
        # final_z_location = self.z_height * self.z_conversion_factor
     
        # self.final_move = np.linspace(
        #     np.array([final_x_location, final_y_location, final_z_location, 0]),
        #     np.zeros(4),
        #     num=self.x_pixels
        # )
        
        
       

    def save_params(self, save_name):
        pass
   


