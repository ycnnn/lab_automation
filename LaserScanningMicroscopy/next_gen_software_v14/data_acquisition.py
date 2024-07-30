import numpy as np
from daq_driver import daq_interface


class Data_acquisitor():

    def __init__(self, position_parameters, scan_parameters):

        self.position_parameters = position_parameters
        self.scan_parameters = scan_parameters
        self.DAQ_output_data = position_parameters.DAQ_output_data
        self.frequency = 1/(scan_parameters.point_time_constant * self.position_parameters.x_pixels)
        self.retrace_frequency = 1/(scan_parameters.retrace_point_time_constant * self.position_parameters.x_pixels)


    
    def run(self, scan_index, retrace=False):

        scan_frequency = self.frequency if not retrace else self.retrace_frequency
    
        DAQ_output_data = self.DAQ_output_data[:,scan_index,:].T


        DAQ_input_data = daq_interface(ao0_1_write_data=DAQ_output_data, 
                      frequency=scan_frequency,
                      input_mapping=self.scan_parameters.input_mapping,
                    DAQ_name=self.scan_parameters.DAQ_name
                    )
        
        shrinked_DAQ_input_data = np.mean(DAQ_input_data[:,:,np.newaxis].reshape(len(self.scan_parameters.input_mapping),-1,2), axis=2)
        # shrinked_DAQ_input_data of shape (DAQ_input_channel_num, scan_parameter.x_pixels)
        return shrinked_DAQ_input_data
    
    
    
    def move_origin(self, initialize=True):
        if initialize:
            DAQ_output_data = self.position_parameters.initial_move
            _ = daq_interface(ao0_1_write_data=DAQ_output_data, 
                        frequency=self.frequency,
                        input_mapping=["ai1", "ai4", "ai20"],
                        DAQ_name=self.scan_parameters.DAQ_name
                        )
            print('Initialization finished! Scan started.')
        else:
            DAQ_output_data = self.position_parameters.final_move
            _ = daq_interface(ao0_1_write_data=DAQ_output_data, 
                        frequency=self.frequency,
                        input_mapping=["ai1", "ai4", "ai20"],
                        DAQ_name=self.scan_parameters.DAQ_name
                        )
            print('Scan finished!')
        
        

