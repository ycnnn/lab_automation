import numpy as np
from daq_driver import daq_interface
from SRS import set_lockin_ready


class Data_acquisitor():

    def __init__(self, position_parameters, scan_parameters):
        self.position_parameters = position_parameters
        self.scan_parameters = scan_parameters

        self.DAQ_output_data = position_parameters.DAQ_output_data
        self.frequency = scan_parameters.frequency

        self.instrument = None
        if scan_parameters.instrument:
            # self.instrument = scan_parameters.instrument.initialize_instrument()
            self.instrument = scan_parameters.instrument.initialize_instrument()
        # self.instrument = None
    #     return instrument
        
    def run(self, 
            scan_index,
            retrace=False):
        
        if self.instrument:
            self.instrument.start_listening()

        shrinked_DAQ_input_data = self.run_with_DAQ(scan_index=scan_index, retrace=retrace)

        input_data = shrinked_DAQ_input_data

        if self.instrument:
            inst_input_data = self.instrument.stop_listening()
            input_data = np.vstack(shrinked_DAQ_input_data, inst_input_data)

        return input_data

    

    def run_with_DAQ(self, scan_index, retrace=False):

        scan_frequency = self.frequency if not retrace else self.scan_parameters.retrace_frequency
    
        DAQ_output_data = self.DAQ_output_data[:,scan_index,:].T


        DAQ_input_data = daq_interface(ao0_1_write_data=DAQ_output_data, 
                      frequency=scan_frequency,
                      input_mapping=self.scan_parameters.input_mapping,
                    # input_mapping=["ai1", "ai4", "ai20"],
                    DAQ_name=self.scan_parameters.DAQ_name
                    )
        # Optionally, some other sensing happens here.
        shrinked_DAQ_input_data = np.mean(DAQ_input_data[:,:,np.newaxis].reshape(len(self.scan_parameters.input_mapping),-1,2), axis=2)
        # shrinked_DAQ_input_data = np.flip(shrinked_DAQ_input_data, axis=1)

        return shrinked_DAQ_input_data
    

    
    
    def move_origin(self, initialize=True):
        if initialize:
            DAQ_output_data = self.position_parameters.initial_move
            _ = daq_interface(ao0_1_write_data=DAQ_output_data, 
                        frequency=self.frequency,
                        input_mapping=["ai1", "ai4", "ai20"],
                        DAQ_name=self.scan_parameters.DAQ_name
                        )
            print('Initialization finished! Scann started.')
        else:
            DAQ_output_data = self.position_parameters.final_move
            _ = daq_interface(ao0_1_write_data=DAQ_output_data, 
                        frequency=self.frequency,
                        input_mapping=["ai1", "ai4", "ai20"],
                        DAQ_name=self.scan_parameters.DAQ_name
                        )
            print('Scan finished!')
        
        

