"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np
import time

# import nidaqmx as ni
# from nidaqmx.constants import WAIT_INFINITELY


# def query_devices():
#     """Queries all the device information connected to the local system."""
#     local = ni.system.System.local()
#     for device in local.devices:
#         print(f"Device Name: {device.name}, Product Type: {device.product_type}")
#         print("Input channels:", [chan.name for chan in device.ai_physical_chans])
#         print("Output channels:", [chan.name for chan in device.ao_physical_chans])


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

    data = data.T
    nsamples = data.shape[1]

    return np.random.random(size=(nsamples, len(input_mapping)))
    

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

    time.sleep(1/frequency)
    return np.flip(sampled_data, axis=1)



def reset_daq(scan_parameters, destination=np.array([0,0,0,0]), ramp_steps=50):

    return np.array([0,0,0,0])




# def lockin_acquision(position_parameters,lockin=None):
    
#     lockin.buffer.stop_capture()
#     x_data = np.array(lockin.buffer.get_capture_data(position_parameters.x_pixels)['X'])
#     y_data = np.array(lockin.buffer.get_capture_data(position_parameters.x_pixels)['Y'])
#     lockin.buffer.start_capture('ONE','SAMP')
#     pass
