"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np
import time
from qcodes.instrument_drivers.stanford_research import SR860

class Lockin:
    def __init__(self, address="USB0::0xB506::0x2000::002765::INSTR", sample_count=128):
        self.address = address
        self.instrument = None
        self.sample_count = sample_count
        self.additional_channel_num = 2
    def initialize_instrument(self):
        # Setup communication to the lockin and perform basic settings
        instrument = SR860('lockin',self.address)
        instrument.input_config('a')
        instrument.buffer.capture_config('X,Y')
        instrument.buffer.set_capture_rate_to_maximum()
        instrument.buffer.set_capture_length_to_fit_samples(self.sample_count)
        return instrument
    def start_listening(self, instrument):
        instrument.buffer.start_capture('ONE','SAMP')
    def stop_listening(self, instrument, scan_parameters):
        instrument.buffer.stop_capture()
        x_data = np.array(instrument.buffer.get_capture_data(scan_parameters.x_pixels)['X'])
        y_data = np.array(instrument.buffer.get_capture_data(scan_parameters.x_pixels)['Y'])
        return np.array([x_data, y_data])



# class Lockin(SR860):
#     def __init__(self, address="USB0::0xB506::0x2000::002765::INSTR", sample_count=128):
#         super().__init__('lockin', address)
#         self.additional_channel_num = 2
#         self.set_ready(sample_count=sample_count)
#     def set_ready(self, sample_count):
#         self.input_config('a')
#         self.buffer.capture_config('X,Y')
#         self.buffer.set_capture_rate_to_maximum()
#         self.buffer.set_capture_length_to_fit_samples(sample_count)
#     def start_listening(self):
#         self.buffer.start_capture('ONE','SAMP')
#     def stop_listening(self, scan_parameters):
#         self.buffer.stop_capture()
#         x_data = np.array(self.buffer.get_capture_data(scan_parameters.x_pixels)['X'])
#         y_data = np.array(self.buffer.get_capture_data(scan_parameters.x_pixels)['Y'])
#         return np.array([x_data, y_data])


