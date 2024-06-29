"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np

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
    # data = np.asarray(data).T
    data = data.T
    nsamples = data.shape[1]

    with ni.Task() as read_task, ni.Task() as write_task:
        for i, o in enumerate(output_mapping):
            aochan = write_task.ao_channels.add_ao_voltage_chan(
                o,
                min_val=devices[o].ao_voltage_rngs[0],
                max_val=devices[o].ao_voltage_rngs[1],
            )
            min_data, max_data = np.min(data[i]), np.max(data[i])
            if ((max_data > aochan.ao_max) | (min_data < aochan.ao_min)).any():
                raise ValueError(
                    f"Data range ({min_data:.2f}, {max_data:.2f}) exceeds output range of "
                    f"{o} ({aochan.ao_min:.2f}, {aochan.ao_max:.2f})."
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
        write_task.write(data.squeeze(), auto_start=False)
        # write_task doesn't start at read_task's start_trigger without this
        write_task.start()
        # do not time out for long inputs
        indata = read_task.read(nsamples, timeout=WAIT_INFINITELY)

    return np.asarray(indata).T


def generate_ao_data_xy_scan(ao_0_data_array, ao_1_data_array, index,pixels):

    # ao_0_data_array,ao_0_data_array: (pixels x picles) np array
    ao_0_shape = ao_0_data_array.shape
    ao_1_shape = ao_1_data_array.shape
    if ao_0_shape != ao_1_shape:
        print('Error: incorrect ao data. Check data shape')
    if ao_0_shape[0] != pixels or ao_0_shape[1] != pixels:
        print('Error: incorrect ao data. Check data shape')

    ao_0_data = ao_0_data_array[index]
    ao_1_data = ao_1_data_array[index]
    return np.array([ao_0_data,ao_1_data]).T


def generate_ao_data_xy_scan_with_sync_channel(ao_0_data_array, ao_1_data_array, index,pixels):
    # Genarates data to be sent to ao channels (XY control + TTL channel).
    # Note! SRS lockin only detects the falling edge.
    # So it is necessary to double the signal samples. For ao_0 and ao_1 channel, we just repeat. 

    ao_0_shape = ao_0_data_array.shape
    ao_1_shape = ao_1_data_array.shape
    if ao_0_shape != ao_1_shape:
        print('Error: incorrect ao data. Check data shape')
    if ao_0_shape[0] != pixels or ao_0_shape[1] != pixels:
        print('Error: incorrect ao data. Check data shape')

    ao_0_data = ao_0_data_array[index]
    ao_1_data = ao_1_data_array[index]
    ao_0_data_sync = np.repeat(ao_0_data.reshape(-1,1), repeats=2, axis=0).reshape(-1)
    ao_1_data_sync = np.repeat(ao_1_data.reshape(-1,1), repeats=2, axis=0).reshape(-1)
    ttl = 2.5*(1-np.arange(2*pixels)%2)
    return np.array([ao_0_data_sync,ao_1_data_sync,ttl]).T

def generate_ao_data(index,pixels):
    # Genarates data to be sent to ao channels (XY control only). 
    ao_0_data = np.sin(np.linspace(0,np.pi,pixels)) * 0.2 *np.abs(index - pixels/2)/(pixels)
    ao_1_data = np.cos(np.linspace(0,np.pi,pixels)) * 0.2 *np.abs(index - pixels/2)/(pixels)
    return np.array([ao_0_data,ao_1_data]).T


def daq_interface(ao0_1_write_data,frequency,
                  input_mapping=["Dev1/ai0", "Dev1/ai4", "Dev1/ai20"],):
    pixels = len(ao0_1_write_data)
    # Be careful. The input argument frequency is line scan frequency
    # Total time for executing one line = 1/frequency
    # Total time = nsamples / samplerate = pixels / samplerate
    # -> samplerate = pixels * frequency

    indata = playrec(
        ao0_1_write_data,
        samplerate=pixels*frequency,
        input_mapping=input_mapping,
        output_mapping=["Dev1/ao0","Dev1/ao1"],
    )
    sampled_data = indata.T
    return np.flip(sampled_data[0]), np.flip(sampled_data[1]), np.flip(sampled_data[2])


def daq_interface_sync(ao0_1_write_data,frequency,
                  input_mapping=["Dev1/ai0", "Dev1/ai4", "Dev1/ai20"],
                  lockin=None):
    ao_output_length = len(ao0_1_write_data)
    pixels = int(ao_output_length/2)
    # Same as daq_interface, but with added TTL channel 
    # ao1, ao1 -> X,Y scan
    # ao3 -> TTL output
    # Important! The output sample number are doubled. To keep the frequency, double the sampleing rate
    # Also, returned ai data is also doubed in size. Remember to rescale them back
    if not lockin:
        print('Lockin reference not correct.')
        return
    lockin.buffer.start_capture('ONE','SAMP')
    #####################################################################################    
    indata = playrec(
        ao0_1_write_data,
        samplerate=pixels*frequency*2,
        input_mapping=input_mapping,
        output_mapping=["Dev1/ao0","Dev1/ao1",'Dev1/ao3'])
    #####################################################################################
    lockin.buffer.stop_capture()
    sampled_data = indata.T

    x_data = np.array(lockin.buffer.get_capture_data(pixels)['X'])
    y_data = np.array(lockin.buffer.get_capture_data(pixels)['Y'])

    return (np.mean(np.flip(sampled_data[0]).reshape(-1,2), axis=1), 
            np.mean(np.flip(sampled_data[1]).reshape(-1,2), axis=1), 
            np.mean(np.flip(sampled_data[2]).reshape(-1,2), axis=1),
            x_data,
            y_data)
