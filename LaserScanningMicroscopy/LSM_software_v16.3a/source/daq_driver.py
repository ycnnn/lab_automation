"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np
import time

import nidaqmx as ni
from nidaqmx.constants import WAIT_INFINITELY


def query_devices():
    """Queries all the device information connected to the local system."""
    local = ni.system.System.local()
    for device in local.devices:
        print(f"Device Name: {device.name}, Product Type: {device.product_type}")
        print("Input channels:", [chan.name for chan in device.ai_physical_chans])
        print("Output channels:", [chan.name for chan in device.ao_physical_chans])


def playrec(data, samplerate, input_mapping, output_mapping):
    """Simultaneous playback and recording though NI device.

    Parameters:
    -----------
    data: array_like, shape (nsamples, len(output_mapping))
      Data to be send to output channels.
    samplerate: int
      Samplerate
    input_mapping: list of str
      Input device channels
    output_mapping: list of str
      Output device channels

    Returns
    -------
    ndarray, shape (nsamples, len(input_mapping))
      Recorded data

    """
    devices = ni.system.System.local().devices
    # print(data.shape)
    data = data.T
    nsamples = data.shape[1]
    # print(data.shape)


    with ni.Task() as read_task, ni.Task() as write_task:
        for i, o in enumerate(output_mapping):
            aochan = write_task.ao_channels.add_ao_voltage_chan(
                o,
                min_val=devices[o].ao_voltage_rngs[0],
                max_val=devices[o].ao_voltage_rngs[1],
            )
            min_data, max_data = (np.min(data[i]), np.max(data[i]))
            if ((max_data > min(aochan.ao_max, 10.0)) | (min_data < max(aochan.ao_min, -0.01))).any():
                raise ValueError(
                    f"Data range ({min_data:.2f}, {max_data:.2f}) exceeds output range. \nThe output range for DAQ is {aochan.ao_min:.2f} to {aochan.ao_max:.2f}; \nThe pizeo scanner will only accept voltages from 0.0 to 10.0."
                )
        for i in input_mapping:
            read_task.ai_channels.add_ai_voltage_chan(i)

        for task in (read_task, write_task):
            task.timing.cfg_samp_clk_timing(
                rate=samplerate, source="OnboardClock", samps_per_chan=nsamples
            )

        # trigger write_task as soon as read_task starts
        write_task.triggers.start_trigger.cfg_dig_edge_start_trig(
            read_task.triggers.start_trigger.term
        )
        # squeeze as Task.write expects 1d array for 1 channel
        write_task.write(
            # np.ascontiguousarray(data),
            np.ascontiguousarray(data.squeeze()), 
                         auto_start=False)
        # write_task doesn't start at read_task's start_trigger without this
        write_task.start()
        # do not time out for long inputs
        indata = read_task.read(nsamples, timeout=WAIT_INFINITELY)

    return np.asarray(indata).T
    

def daq_interface(ao0_1_write_data,
                  frequency,
                  input_mapping,
                  DAQ_name,
                  output_mapping=['ao0', 'ao1', 'ao2', 'ao3'],
                  ):
    pixels = len(ao0_1_write_data)
    # print(f'Pixels:{pixels}')
    # print(f'Shape:{ao0_1_write_data.shape}')
    # Be careful. The input argument frequency is line scan frequency
    # Total time for executing one line = 1/frequency
    # Total time = nsamples / samplerate = pixels / samplerate
    # -> samplerate = pixels * frequency
    input_mapping_full_path = [DAQ_name + '/'+ channel_name for channel_name in input_mapping]
    output_mapping_full_path = [DAQ_name + '/'+ channel_name for channel_name in output_mapping]
    indata = playrec(
        ao0_1_write_data,
        samplerate=pixels*frequency,
        input_mapping=input_mapping_full_path,
        output_mapping=output_mapping_full_path,
    )
    sampled_data = indata.T
    # print(sampled_data.shape, flush=True)

    # Something needs to be done here!

    # time.sleep(1/frequency)
    if len(sampled_data.shape) == 1:
        sampled_data = sampled_data.reshape(-1,1)
    return np.flip(sampled_data, axis=1)
    # return sampled_data

def set_z_height(scan_parameters, position_parameters):
    if position_parameters.z_center < -0.25 or position_parameters.z_center > 49.0:
        print('Error: input z height is beyond the piezo stage travel range.')
        return
    with ni.Task() as write_task:
        for channel in [0,1,2,3]:
            write_task.ao_channels.add_ao_voltage_chan(scan_parameters.DAQ_name + "/ao" + str(channel),
                                        min_val=-10, max_val=10)
            # write_task.ao_channels.add_ao_voltage_chan(scan_parameters.DAQ_name + "/ao1",
            #                             min_val=-10, max_val=10)
            # write_task.ao_channels.add_ao_voltage_chan(scan_parameters.DAQ_name + "/ao2",
            #                             min_val=-10, max_val=10)
            # write_task.ao_channels.add_ao_voltage_chan(scan_parameters.DAQ_name + "/ao2",
            #                             min_val=-10, max_val=10)
        write_task.write(position_parameters.center_output)
    print(f'Stage Z height has been moved to {position_parameters.z_center}.\n')
    return

def read_daq_output(scan_parameters):

    with ni.Task() as read_task:
        for channel_id in [0,1,2,3]:
            read_task.ai_channels.add_ai_voltage_chan(scan_parameters.DAQ_name + f"/_ao{channel_id}_vs_aognd",
                                    min_val=-10, max_val=10)
        result = np.array(read_task.read())
    return result


def reset_daq(scan_parameters, destination=np.array([0,0,0,0]), ramp_steps=50):

    # with ni.Task() as read_task:
    #     for channel_id in [0,1,2,3]:
    #         read_task.ai_channels.add_ai_voltage_chan(scan_parameters.DAQ_name + f"/_ao{channel_id}_vs_aognd",
    #                                 min_val=-10, max_val=10)
    result = read_daq_output(scan_parameters)
    
    ramp_output_data = np.linspace(
        result, 
        destination,
        num=ramp_steps)
    _ = daq_interface(ao0_1_write_data=ramp_output_data,
                frequency=2,
                input_mapping=['ai0', 'ai1'],
                DAQ_name=scan_parameters.DAQ_name)
    
    resetted_result = read_daq_output(scan_parameters)

    return resetted_result




def lockin_acquision(position_parameters,lockin=None):
    
    lockin.buffer.stop_capture()
    x_data = np.array(lockin.buffer.get_capture_data(position_parameters.x_pixels)['X'])
    y_data = np.array(lockin.buffer.get_capture_data(position_parameters.x_pixels)['Y'])
    lockin.buffer.start_capture('ONE','SAMP')
    pass
