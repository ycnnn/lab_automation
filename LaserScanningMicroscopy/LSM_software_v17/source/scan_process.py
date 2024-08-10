import numpy as np
import multiprocessing as mp
from contextlib import ExitStack
# import multiprocess as mp
# import sys
######################################################################
# Custom dependencies
# from source.inst_driver import External_instrument
from source.app import QPlot
from source.app import QPlot
from source.data_acquisition import Data_acquisitor
from source.daq_driver import reset_daq
import source.inst_driver as inst_driver
from source.plot_process import Data_receiver




class LSM_scan:
    
    def __init__(self,
                  position_parameters, 
                  scan_parameters, 
                  display_parameters,
                  instruments=[]):
          
        self.scan_parameters = scan_parameters
        self.position_parameters = position_parameters
        self.display_parameters = display_parameters

        self.instruments = instruments

        # Mandatory code. There MUST be at least one external instrument present dring the scan.
        empty_instr = inst_driver.EmptyInstrument(
            address='',
                    position_parameters=position_parameters,
                    scan_parameters=scan_parameters
                    )
        
        instruments.append(empty_instr)






        self.line_width = self.position_parameters.x_pixels
        self.total_scan_num = 2 * self.position_parameters.y_pixels

        self.acquisitor = Data_acquisitor(position_parameters,scan_parameters)

        print('Acuisitor initilized!')

        self.channel_num = self.scan_parameters.channel_num

        for instrument in self.instruments:
            self.channel_num += instrument.channel_num

        self.start_scan()


    def start_scan(self):

        print('Channel num: ' + str(self.channel_num))

        


        # mp.freeze_support()
        self.out_pipe, self.in_pipe = mp.Pipe(duplex=True)

        self.data_receiver = Data_receiver(position_parameters=self.position_parameters,
                                    scan_parameters=self.scan_parameters, 
                                    display_parameters=self.display_parameters,
                                    channel_num=self.channel_num,
                                    pipe=self.in_pipe)
        
        self.data_receiver.start()

        ########################################################################
        # Initialize the system position
        reset_daq(self.scan_parameters, destination=self.position_parameters.center_output)
        self.acquisitor.move_origin(initialize=True)
        ########################################################################
     
    
        instrument_manager = [
                instrument.initialize_and_quit for instrument in self.instruments]
        
        scan_manager = [instrument.scan for instrument in self.instruments]

        with ExitStack() as stack:
            _ = [stack.enter_context(instr()) for instr in instrument_manager]

      

            for total_scan_index in range(self.total_scan_num):
                    auxiliary_scan_info = {'total_scan_index': total_scan_index}
                        
                    with ExitStack() as stack:
                        _ = [stack.enter_context(
                                instr_scan(**auxiliary_scan_info)
                                ) for instr_scan in scan_manager]
                        if total_scan_index % 2 == 0:
                            data = self.acquisitor.run(total_scan_index)
                        else:
                            data = self.acquisitor.run(total_scan_index, retrace=True)

                    instr_data = np.vstack([
                            resource.data for resource in self.instruments
                            ])

                    data = np.vstack((data, instr_data))

                      

                    self.out_pipe.send(data)

                    status = self.out_pipe.recv()
                    if not status:
                        raise Warning('Possible data loss: Sender not received confirmation from receiver')


            self.acquisitor.move_origin(initialize=False)

        self.data_receiver.join()

        
