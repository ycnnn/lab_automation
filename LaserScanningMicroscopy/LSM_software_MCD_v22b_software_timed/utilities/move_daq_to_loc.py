import os
import time
import itertools
import numbers
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from source.params.position_params import Position_parameters
# from source.params.scan_params import Scan_parameters
# from source.daq_driver_simulated import reset_daq, set_z_height, read_daq_output
import nidaqmx as ni
import numpy as np
from nidaqmx.constants import Edge, AcquisitionType, TaskMode, WAIT_INFINITELY
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter


def set_pos(DAQ_name, position):
    x,y,z  = position
    if z < -0.25 or z > 49.5:
        print('Error: input z height is beyond the piezo stage travel range.')
        return
    if x < -0.25 or x > 99.5 or y < -0.25 or y > 99.5:
        print('Error: input x or y is beyond the piezo stage travel range.')
        return
    xy_conversion_factor = 0.10
    z_conversion_factor = 0.20
    output = (x * xy_conversion_factor, y * xy_conversion_factor, z * z_conversion_factor)
    with ni.Task() as write_task:
        for channel in [0,1,2]:
            write_task.ao_channels.add_ao_voltage_chan(DAQ_name + "/ao" + str(channel),
                                        min_val=-10, max_val=10)
        write_task.write(np.ascontiguousarray(output))
    print(f'Stage position has been moved to ')
    print(position)
    print('\n')
    return

def read_daq_output(DAQ_name='Dev2'):

    with ni.Task() as read_task:
        for channel_id in [0,1,2]:
            read_task.ai_channels.add_ai_voltage_chan(DAQ_name + f"/_ao{channel_id}_vs_aognd",
                                    min_val=-10, max_val=10)
        result = np.array(read_task.read())
    return result


def main():
    while True:
        user_input = input("Enter the x,y,z position in microns, such as 50,50,0. Or press 'R' to reset, or press Enter to quit:\n")
        
        # Check for empty content
        if user_input.strip() == "":
            daq_output = read_daq_output(DAQ_name='Dev2')
            print('DAQ output is: ')
            print(daq_output)
            time.sleep(5)
            print("\nExiting the program.")
            break
        
        # Check for the letter 'R'
        elif user_input.strip().upper() == "R":
            print("Reset DAQ:")
            set_pos(DAQ_name='Dev2', position=(0,0,0))
            daq_output = read_daq_output(DAQ_name='Dev2')
            print('DAQ output has been set to: ')
            print(daq_output)
            print('\n')
        
        # Check for tuple input
        else:
            try:
                # Evaluate the input as a tuple
                evaluated_input = eval(user_input)
                if isinstance(evaluated_input, tuple) and len(evaluated_input) == 3:
                    set_pos(DAQ_name='Dev2', position=evaluated_input)
                    daq_output = read_daq_output(DAQ_name='Dev2')
                    print('DAQ output has been set to: ')
                    print(daq_output)
                    print('\n')
                    # Add your logic here for a valid tuple
                else:
                    print("Incorrect input. Please enter a three-element tuple, 'R', or press Enter.")
            except:
                print("Incorrect input. Please enter a three-element tuple, 'R', or press Enter.")

if __name__ == "__main__":
    main()


