import numpy as np
from qcodes.instrument_drivers.stanford_research import SR860

def set_lockin_ready(address="USB0::0xB506::0x2000::002765::INSTR",
                     sample_count=128):
    # Setup communication to the lockin and perform basic settings
    lockin = SR860('lockin',"USB0::0xB506::0x2000::002765::INSTR")
    lockin.input_config('a')
    lockin.buffer.capture_config('X,Y')
    lockin.buffer.set_capture_rate_to_maximum()
    lockin.buffer.set_capture_length_to_fit_samples(sample_count)
    return lockin

def set_lockin_output(lockin,frequency=201700, amplitude=0.1, dc=0):
    # Set up lockin output, frequency, amplitude, dc
    pass
# def get_lockin_data(lockin,sample_count):
#     x_data = np.array(lockin.buffer.get_capture_data(sample_count)['X'])
#     y_data = np.array(lockin.buffer.get_capture_data(sample_count)['Y'])
#     return x_data, y_data

def lockin_start_listen(lockin):
    lockin.buffer.start_capture('ONE','SAMP')

def lockin_stops_listen(lockin, scan_parameters):
    lockin.buffer.stop_capture()
    x_data = np.array(lockin.buffer.get_capture_data(scan_parameters.x_pixels)['X'])
    y_data = np.array(lockin.buffer.get_capture_data(scan_parameters.x_pixels)['Y'])

class Lockin(SR860):
    def __init__(self, address="USB0::0xB506::0x2000::002765::INSTR", sample_count=128):
        super().__init__('lockin', address)
        self.set_ready(sample_count=sample_count)
    def set_ready(self, sample_count):
        self.input_config('a')
        self.buffer.capture_config('X,Y')
        self.buffer.set_capture_rate_to_maximum()
        self.buffer.set_capture_length_to_fit_samples(sample_count)
    def start_listen(self):
        self.buffer.start_capture('ONE','SAMP')
    def stops_listen(self, scan_parameters):
        self.buffer.stop_capture()
        x_data = np.array(self.buffer.get_capture_data(scan_parameters.x_pixels)['X'])
        y_data = np.array(self.buffer.get_capture_data(scan_parameters.x_pixels)['Y'])

