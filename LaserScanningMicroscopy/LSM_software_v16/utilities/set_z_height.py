import os
import itertools
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from source.params.position_params import Position_parameters
from source.params.scan_params import Scan_parameters
# from source.daq_driver_simulated import reset_daq, set_z_height, read_daq_output
from source.daq_driver import reset_daq, set_z_height, read_daq_output

if __name__=='__main__':
    message = 'Enter command.\nEnter a number to move the stage height;\nEnter R for resetting the DAQ;\nPress enter to switch the stage height between the last two values you entered.\nEnter anything else to quit the code.\n\n'

    command = input(message).capitalize()
    scan_parameters = Scan_parameters()
    heights = [0,0]
    alter_index = 1

    while True:

        try:
            z_height = float(command)
            position_parameters = Position_parameters(z_center=float(z_height))
            set_z_height(scan_parameters=scan_parameters,
                                    position_parameters=position_parameters)
            heights.pop(0)
            heights.append(z_height)
        except:
            if command == 'R':
                reset_daq(scan_parameters=scan_parameters)
                print('DAQ output has been reset to (0,0,0,0)\n')
            elif len(command) == 0:
                print('Start alternating between the last two Z heights you entered. To switch, press Enter. To quit, press Q.\n')
                while True:
                    # Move
                    new_command = input('Switch the height by press Enter, press any other key to quit\n')
                    alter_index += 1
                    if new_command != "":
                        break
                    z_height = heights[int(alter_index % 2)]
                    position_parameters = Position_parameters(z_center=float(z_height))
                    set_z_height(scan_parameters=scan_parameters,
                                            position_parameters=position_parameters)
            else:
                break
        command = input(message).capitalize()

                    
