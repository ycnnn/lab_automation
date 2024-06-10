import numpy as np
from ng_daq_driver import daq_interface


class Data_acquisitor():

    def __init__(self, position_parameters, scan_parameters):
        self.position_parameters = position_parameters
        self.DAQ_output_data = np.array([position_parameters.x_coordinates, 
                                         position_parameters.y_coordinates])
        self.frequency = scan_parameters.frequency
        
    def run(self, scan_index):
    
        DAQ_output_data = self.DAQ_output_data[:,scan_index,:].T
        DAQ_input_data = daq_interface(ao0_1_write_data=DAQ_output_data, 
                      frequency=self.frequency,
                      input_mapping=["ai1", "ai4", "ai20"],
                    )
        # Optionally, some other sensing happens here.
        return DAQ_input_data
    def move_origin(self, initialize=True):
        if initialize:
            DAQ_output_data = self.position_parameters.initial_move
        else:
            DAQ_output_data = self.position_parameters.final_move
        _ = daq_interface(ao0_1_write_data=DAQ_output_data, 
                        frequency=self.frequency,
                        input_mapping=["ai1", "ai4", "ai20"],
                        )
        

