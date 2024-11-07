import sys, os
from app import LSMLivePlot
from PySide6 import QtWidgets
import numpy as np
import time, random
from contextlib import ExitStack
import instruments as inst_driver
from log_config import setup_logging

class LSM_single_scan:
    def __init__(self,
                 instruments=[],
                 scan_parameters=None,
                 simulate=True
                 ):
        self.scan_parameters = scan_parameters
        self.instruments = instruments
        self.simulate = simulate
        
         # Mandatory code. There MUST be at least one external instrument present dring the scan.
        empty_instr = inst_driver.EmptyInstrument(
            address='',
            scan_parameters=scan_parameters)
        self.instruments.append(empty_instr)

        self.channel_num = 0

        for instrument in self.instruments:
            self.channel_num += instrument.channel_num

        self.data = np.zeros(shape=(self.channel_num, self.scan_parameters.steps))
        # Set up the logging process
        self.logger = setup_logging(self.scan_parameters.save_destination)
        self.start_scan()
        self.save()

        

    def start_ui(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = LSMLivePlot(channel_num=self.channel_num, 
                                       steps=self.scan_parameters.steps)
        self.main_window.show()
    
    def start_scan(self):

        self.logger.info('Scan started.\n\n')

        instrument_manager = [
                instrument.initialize_and_quit for instrument in self.instruments]
        
        scan_manager = [instrument.scan for instrument in self.instruments]

        auxiliary_init_info = {'logger': self.logger}

        self.start_ui()

        with ExitStack() as init_stack:
            _ = [init_stack.enter_context(
                    instr(**auxiliary_init_info)
                    ) for instr in instrument_manager]

            for scan_index in range(self.scan_parameters.steps):
                    
                    # time.sleep(0.01)

                    auxiliary_scan_info = {'scan_index': scan_index}
                        
                    with ExitStack() as scan_stack:
                        _ = [scan_stack.enter_context(
                                instr_scan(**auxiliary_scan_info)
                                ) for instr_scan in scan_manager]
                        
                 
                    instr_data = np.concatenate([
                            resource.data for resource in self.instruments
                            ])
                    self.data[:,scan_index] = instr_data

                    # Update
                    self.main_window.update_data(scan_index, self.data)
                    self.app.processEvents()
                                
        
        self.logger.info('\n\nScan finished.\n\n')
        self.app.exit()

    def save(self):
        pass

class Position_parameters:
    def __init__(self, center=(0,0,0), angle=0, length=0, steps=10, return_to_zero=False):

        self.return_to_zero = return_to_zero
        self.xy_conversion = 0.10
        self.z_conversion = 0.20

        self.angle_radian = angle / 180.0 * np.pi
        self.x_center, self.y_center, self.z_center = center
        self.x_unrot = np.linspace(-length/2, length/2, num=steps)
        self.y_unrot = np.zeros(shape=steps) * self.y_center
        self.z = np.ones(shape=steps) * self.z_center
        self.x_rot = np.cos(self.angle_radian) * self.x_unrot + np.sin(self.angle_radian) * self.y_unrot + self.x_center
        self.y_rot = - np.sin(self.angle_radian) * self.x_unrot + np.cos(self.angle_radian) * self.y_unrot + self.y_center

        self.center_output = np.array([self.x_center * self.xy_conversion, 
                              self.y_center * self.xy_conversion, 
                              self.z_center * self.z_conversion])
        self.DAQ_output_data = np.array([self.x_rot * self.xy_conversion, 
                           self.y_rot * self.xy_conversion, 
                           self.z * self.z_conversion])

class Scan_paramters:
    def __init__(self, 
                 steps=500, 
                 save_destination=None,
                 position_parameters=None):
        self.steps = steps
        self.save_destination = save_destination if save_destination else os.path.dirname(os.path.realpath(__file__))
        self.position_parameters = position_parameters

def main():

    instruments = []
    steps = 100
    position_parameters = Position_parameters(steps=steps)
    scan_parameters = Scan_paramters(steps=steps, position_parameters=position_parameters)
    

    daq = inst_driver.DAQ(
                    scan_parameters=scan_parameters,
                    input_mapping=['ai0', 'ai1'],
                    )
    instruments.append(daq)

    smu1 = inst_driver.SMU(scan_parameters=scan_parameters,
                 address="USB0::0x05E6::0x2450::04096331::INSTR",
                 mode='Force_V_Sense_I',
                 **{'Force':[-20,20]})
    instruments.append(smu1)



    sim_instr = inst_driver.SimulatedInstrument(
        address='', scan_parameters=scan_parameters)
    instruments.append(sim_instr)



    # lockin = inst_driver.Lockin(scan_parameters=scan_parameters,
    #                             **{
    #                                 'time_constant_level':0, 
    #                                 'volt_input_range':0, 
    #                                 'signal_sensitivity':0,
    #                 })
    # instruments.append(lockin)

    # laser = inst_driver.LaserDiode(scan_parameters=scan_parameters, **{'current':[0,0.01]})
    # instruments.append(laser)


    LSM_single_scan(
             scan_parameters=scan_parameters,
             instruments=instruments,
             simulate=True)





if __name__ == "__main__":
    main()
