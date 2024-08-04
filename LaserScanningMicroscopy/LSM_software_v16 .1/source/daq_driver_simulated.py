"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np
import time

# Note: this file is only used to test the non-DAQ-related part of the code.
# In real experiment, refer to daq_driver instead of this file when calling DAQ functions in other files.



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
    # return np.zeros(shape=(nsamples, len(input_mapping)))
    

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


def set_z_height(scan_parameters, position_parameters):
    if position_parameters.z_center < -0.25 or position_parameters.z_center > 49.0:
        print('Error: input z height is beyond the piezo stage travel range.')
        return
    print(f'Stage Z height has been moved to {position_parameters.z_center}.\n')
    return

def read_daq_output(scan_parameters):
    return np.array([1,1,1,1])
