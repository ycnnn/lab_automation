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

np.set_printoptions(precision=3)

def set_pos(DAQ_name, position, xy_conversion_factor, z_conversion_factor):
    x,y,z  = position
    if z < -0.25 or z > 49.5:
        print('Error: input z height is beyond the piezo stage travel range.')
        return
    if x < -0.25 or x > 99.5 or y < -0.25 or y > 99.5:
        print('Error: input x or y is beyond the piezo stage travel range.')
        return
    
    output = (x * xy_conversion_factor, y * xy_conversion_factor, z * z_conversion_factor)
    with ni.Task() as write_task:
        for channel in [0,1,2]:
            write_task.ao_channels.add_ao_voltage_chan(DAQ_name + "/ao" + str(channel),
                                        min_val=-10, max_val=10)
        write_task.write(np.ascontiguousarray(output))

    # np.set_printoptions(precision=3)
    print(f'Stage position has been set to', end=' ')
    print(np.array(position))
    print('\n')
    return

def read_pos(xy_conversion_factor, z_conversion_factor, DAQ_name='Dev2', display=True):

    with ni.Task() as read_task:
        for channel_id in [0,1,2]:
            read_task.ai_channels.add_ai_voltage_chan(DAQ_name + f"/_ao{channel_id}_vs_aognd",
                                    min_val=-10, max_val=10)
        result = np.array(read_task.read())
    current_pos = np.array((result[0]/xy_conversion_factor, result[1]/xy_conversion_factor, result[2]/z_conversion_factor))
    if display:
        # np.set_printoptions(precision=3)
        print('Current stage position reads:', end=' ')
        print(current_pos)
        print('\n')

    return current_pos


def main():

    xy_conversion_factor = 0.10
    z_conversion_factor = 0.20

    while True:
        user_input = input('''
        Control the stage position. Options:
        - Press R: reset the stage position to  (0 um, 0 um, 0 um).
        - Press Enter: read current stage position.
        - Enter ONE number: set the z height of the stage. The x, y position of the stage will remain unchanged.
        - Enter THREE numbers, seperated with comma, such as 20,20,20: set the x, y, z position of the stage.
        
        ''')
        # Check for empty content
        print('\n')
        if user_input.strip() == "":
            current_pos = read_pos(DAQ_name='Dev2',
                                    xy_conversion_factor=xy_conversion_factor, 
                                    z_conversion_factor=z_conversion_factor)
            # time.sleep(5)
            # print("Exiting the program.")
            # break
            continue
        
        # Check for the letter 'R'
        elif user_input.strip().upper() == "R":
            print("Reset DAQ: ", end=' ')
            set_pos(DAQ_name='Dev2', position=(0,0,0), 
                    xy_conversion_factor=xy_conversion_factor, 
                    z_conversion_factor=z_conversion_factor)
            current_pos = read_pos(DAQ_name='Dev2',
                                    xy_conversion_factor=xy_conversion_factor, 
                                    z_conversion_factor=z_conversion_factor)
        
        # Check for tuple input
        else:
            try:
                # Evaluate the input as a tuple
                evaluated_input = eval(user_input)

                if isinstance(evaluated_input, tuple) and len(evaluated_input) == 3:
                    set_pos(DAQ_name='Dev2', position=evaluated_input,
                            xy_conversion_factor=xy_conversion_factor, 
                            z_conversion_factor=z_conversion_factor)
                    current_pos = read_pos(DAQ_name='Dev2',
                                            xy_conversion_factor=xy_conversion_factor, 
                                            z_conversion_factor=z_conversion_factor)
                  

                elif isinstance(evaluated_input, numbers.Number):
                    current_pos = read_pos(DAQ_name='Dev2',
                                            xy_conversion_factor=xy_conversion_factor, 
                                            z_conversion_factor=z_conversion_factor,
                                            display=False)
                    set_pos(DAQ_name='Dev2', position=(current_pos[0], current_pos[1], evaluated_input),
                            xy_conversion_factor=xy_conversion_factor, 
                            z_conversion_factor=z_conversion_factor)
                    current_pos = read_pos(DAQ_name='Dev2',
                                            xy_conversion_factor=xy_conversion_factor, 
                                            z_conversion_factor=z_conversion_factor)

                else:
                    print("Incorrect input. Please enter a three-element tuple, 'R', or press Enter.")
            except:
                print("Incorrect input. Please enter a three-element tuple, 'R', or press Enter.")

if __name__ == "__main__":
    main()


