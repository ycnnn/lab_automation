import os
import itertools
import numbers
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from source.parameters import Position_parameters
# from source.params.scan_params import Scan_parameters
# from source.daq_driver_simulated import reset_daq, set_z_height, read_daq_output
import nidaqmx as ni
import numpy as np
from nidaqmx.constants import Edge, AcquisitionType, TaskMode, WAIT_INFINITELY
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter


def set_z_height(DAQ_name, position_parameters):
    if position_parameters.z_center < -0.25 or position_parameters.z_center > 49.0:
        print('Error: input z height is beyond the piezo stage travel range.')
        return
    with ni.Task() as write_task:
        for channel in [0,1,2]:
            write_task.ao_channels.add_ao_voltage_chan(DAQ_name + "/ao" + str(channel),
                                        min_val=-10, max_val=10)
        write_task.write(np.ascontiguousarray(position_parameters.center_output))
    print(f'Stage Z height has been moved to {position_parameters.z_center}.\n')
    return

def read_daq_output(DAQ_name='Dev2'):

    with ni.Task() as read_task:
        for channel_id in [0,1,2]:
            read_task.ai_channels.add_ai_voltage_chan(DAQ_name + f"/_ao{channel_id}_vs_aognd",
                                    min_val=-10, max_val=10)
        result = np.array(read_task.read())
    return result


def reset_daq(destination=np.array([0,0,0]), ramp_steps=50, DAQ_name='Dev2'):

    result = read_daq_output(DAQ_name=DAQ_name)
    ramp_output_data = np.linspace(result, destination,num=ramp_steps).T
    with ni.Task() as write_task:
        for channel in [0,1,2]:
            write_task.ao_channels.add_ao_voltage_chan(DAQ_name + "/ao" + str(channel), min_val=-10, max_val=10)
        # write_task.timing.cfg_samp_clk_timing(ramp_steps, sample_mode=AcquisitionType.FINITE, samps_per_chan=ramp_steps)
        ao_writer = AnalogMultiChannelWriter(write_task.out_stream, auto_start=True)
        ao_writer.write_many_sample(np.ascontiguousarray(ramp_output_data))


if __name__=='__main__':
    message = 'Enter command.\nEnter a number to move the stage height;\nEnter R or r for resetting the DAQ;\nEnter anything else to quit the code.\n\n'

    command = input(message).capitalize()
    DAQ_name = 'Dev2'
    heights = [0,0]
    alter_index = 1


    while True:


        try:
            z_height = float(command)
            position_parameters = Position_parameters(z_center=float(z_height))
            set_z_height(DAQ_name=DAQ_name,
                                    position_parameters=position_parameters)
            daq_output = read_daq_output(DAQ_name=DAQ_name)
            print('DAQ output has been set to: ')
            print(daq_output)
            print('\n')
            heights.pop(0)
            heights.append(z_height)

        except ValueError:

            
            if command == 'R':
                reset_daq(DAQ_name=DAQ_name)
                daq_output = read_daq_output(DAQ_name=DAQ_name)
                print('DAQ output has been reset to: ')
                print(daq_output)
                print('\n')

            else:
                break
        command = input(message).capitalize()


                    
