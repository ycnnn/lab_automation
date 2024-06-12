import numpy as np
from daq_driver import daq_interface


class Data_acquisitor():

    def __init__(self, position_parameters, scan_parameters):
        self.position_parameters = position_parameters
        self.scan_parameters = scan_parameters
        # self.DAQ_output_data = np.array([position_parameters.x_coordinates, 
        #                                  position_parameters.y_coordinates,
        #                                  position_parameters.ttl])
        self.DAQ_output_data = position_parameters.DAQ_output_data
        self.frequency = scan_parameters.frequency
        
    def run(self, scan_index):
    
        DAQ_output_data = self.DAQ_output_data[:,scan_index,:].T
        DAQ_input_data = daq_interface(ao0_1_write_data=DAQ_output_data, 
                      frequency=self.frequency,
                      input_mapping=self.scan_parameters.input_mapping,
                    # input_mapping=["ai1", "ai4", "ai20"],
                    DAQ_name=self.scan_parameters.DAQ_name
                    )
        # Optionally, some other sensing happens here.
        shrinked_DAQ_input_data = np.mean(DAQ_input_data[:,:,np.newaxis].reshape(self.scan_parameters.channel_num,-1,2), axis=2)
        return shrinked_DAQ_input_data
    
    def move_origin(self, initialize=True):
        if initialize:
            DAQ_output_data = self.position_parameters.initial_move
        else:
            DAQ_output_data = self.position_parameters.final_move
        _ = daq_interface(ao0_1_write_data=DAQ_output_data, 
                        frequency=self.frequency,
                        input_mapping=["ai1", "ai4", "ai20"],
                        DAQ_name=self.scan_parameters.DAQ_name
                        )
        print('Initialization finished!')
        

