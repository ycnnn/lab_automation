"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np
import pyvisa


class Lockin:
    def __init__(self, address="USB0::0xB506::0x2000::002765::INSTR", sample_count=128):
        self.address = address
        self.instrument = None
        self.sample_count = sample_count
        self.additional_channel_num = 2

    def initialize_instrument(self):
        # Setup communication to the lockin and perform basic settings
        rm = pyvisa.ResourceManager()
        instrument = rm.open_resource('USB0::0xB506::0x2000::002765::INSTR')

        instrument.write('*rst')
        instrument.query('*idn?')
        instrument.write('capturelen 256')
        instrument.write('capturecfg xy')
        instrument.write('rtrg posttl')

        self.instrument = instrument

        # return instrument
    
    def start_listening(self):
        self.instrument.write('capturestart one, samp')

    def stop_listening(self, scan_parameters):
        self.instrument.write('capturestop')
        buffer_len = int(self.instrument.query('captureprog?')[:-1])
        data = np.array(self.instrument.query_binary_values(f'captureget? 0, {buffer_len}')).reshape(-1,2)
        return data
    