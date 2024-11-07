import sys, os
from app import LSMLivePlot
from PySide6 import QtWidgets
import numpy as np
import time, random
from contextlib import ExitStack
from pathlib import Path
import instruments as inst_driver
from log_config import setup_logging
from parameters import Scan_paramters, Position_parameters

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
        self.channel_names = []

        for instrument in self.instruments:
            self.channel_num += instrument.channel_num
            for name in instrument.channel_name_list:
                self.channel_names.append(name)
      

        self.data = np.zeros(shape=(self.channel_num, self.scan_parameters.steps))
        # Set up the logging process
        self.logger = setup_logging(self.scan_parameters.save_destination)
        self.start_scan()
        self.save()

        

    def start_ui(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = LSMLivePlot(channel_num=self.channel_num, 
                                       channel_names=self.channel_names,
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
                    
                    # time.sleep(0.5)

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
        screenshot = self.main_window.grab()
        screenshot.save(self.scan_parameters.save_destination + 'screenshot.png')
        np.save(self.scan_parameters.save_destination + 'data', self.data)
        np.savetxt(self.scan_parameters.save_destination + 'data.csv', self.data.T,
                   header=",".join(self.channel_names),
                   delimiter=',',
                   comments=''
                   )


class Scan_paramters:
    def __init__(self, 
                 scan_id='scan_',
                 steps=500, 
                 save_destination=None,
                 position_parameters=None):
        self.steps = steps
        self.scan_id = scan_id
        self.save_destination = save_destination
        # self.save_destination = save_destination if save_destination else os.path.dirname(os.path.realpath(__file__))
        self.create_path()
        self.position_parameters = position_parameters

    def create_path(self):
        full_path = os.path.realpath(__file__)
        path = str(Path(os.path.dirname(full_path)).parents[0].absolute()) + '/results/' + self.scan_id + '/'
    
        self.save_destination = path if not self.save_destination else self.save_destination
       
        # The following code save the data.
        # In case there is already a filder that hav the same name as the save desitnation,
        # The code will rename the old folder by adding a suffix of "_backup".
        # In cases there is alreay a backup folder, the code will add a number to suffix to identify each backup.
        # For example: if "test" alreay exist, the code will try to move the old data to "text_backup_1"; if "text_backup_1" is also there, the code will try change the identifier to "text_backup_2", "text_backup_3", "text_backup_4" etc.
        # In short, the code NEVER overwrites nor DELETES your data!

        if os.path.exists(self.save_destination):
            # If the directory does not exist, create it

            uniq = 1
            backup_path = path[:-1] + '_backup_' + str(uniq) + '/'
            while os.path.exists(backup_path):
                uniq += 1
                backup_path = path[:-1] + '_backup_' + str(uniq) + '/'
        
            os.rename(self.save_destination, backup_path)

        os.makedirs(self.save_destination)
        
def main():

    instruments = []
    steps = 80
    position_parameters = Position_parameters(steps=steps)
    scan_parameters = Scan_paramters(steps=steps, position_parameters=position_parameters)
    

    daq = inst_driver.DAQ_simulated(
                    scan_parameters=scan_parameters,
                    input_mapping=['ai0'],
                    )
    instruments.append(daq)

    # smu_G = inst_driver.SMU(scan_parameters=scan_parameters,
    #              address="USB0::0x05E6::0x2450::04096331::INSTR",
    #              mode='Force_V_Sense_V',
    #              **{'Source':[-10,10]})
    # instruments.append(smu_G)

    # smu_D = inst_driver.SMU(scan_parameters=scan_parameters,
    #              address="USB0::0x05E6::0x2450::04096333::INSTR",
    #              mode='Force_V_Sense_I',
    #              **{'Source':[-1,1]})
    # instruments.append(smu_D)





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
