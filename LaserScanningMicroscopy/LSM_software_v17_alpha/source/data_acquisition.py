import numpy as np
import os
from source.daq_driver import daq_interface


class Data_acquisitor():

    def __init__(self, position_parameters, scan_parameters):

        self.position_parameters = position_parameters
        self.scan_parameters = scan_parameters
        self.DAQ_output_data = position_parameters.DAQ_output_data
        self.frequency = 1/(scan_parameters.point_time_constant * self.position_parameters.x_pixels)
        self.retrace_frequency = 1/(scan_parameters.retrace_point_time_constant * self.position_parameters.x_pixels)

        print(f'Acuisitor frequency: {self.frequency}' )


    
    def run(self, total_scan_index, retrace=False):
        # Note: the scan index here has different defination than those unsed in external instruments.
        # Here the scan index runs from 0 to 2*scan_num-1,
        # While in external instruments, the scan index runs from 0 to scan_num-1

        scan_frequency = self.frequency if not retrace else self.retrace_frequency
    
        DAQ_output_data = self.DAQ_output_data[:,total_scan_index,:].T


        DAQ_input_data = daq_interface(ao0_1_write_data=DAQ_output_data, 
                      frequency=scan_frequency,
                      input_mapping=self.scan_parameters.input_mapping,
                    DAQ_name=self.scan_parameters.DAQ_name
                    )
        
        shrinked_DAQ_input_data = np.mean(DAQ_input_data[:,:,np.newaxis].reshape(len(self.scan_parameters.input_mapping),-1,2), axis=2)

        return shrinked_DAQ_input_data
    
    
    
    def move_origin(self, initialize=True):
        if initialize:
            DAQ_output_data = self.position_parameters.initial_move
            _ = daq_interface(ao0_1_write_data=DAQ_output_data, 
                        # frequency=self.frequency,
                        frequency=min(1, self.frequency),
                        input_mapping=["ai1", "ai4", "ai20"],
                        DAQ_name=self.scan_parameters.DAQ_name
                        )
            print('Initialization finished! Scan started.')
        else:
            DAQ_output_data = self.position_parameters.final_move
            _ = daq_interface(ao0_1_write_data=DAQ_output_data, 
                        # frequency=self.frequency,
                        frequency=min(1, self.frequency),
                        input_mapping=["ai1", "ai4", "ai20"],
                        DAQ_name=self.scan_parameters.DAQ_name
                        )
            print('Scan finished!')
        
        

