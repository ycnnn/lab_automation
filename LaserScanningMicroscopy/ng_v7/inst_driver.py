"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np
import pyvisa
from contextlib import contextmanager

class External_instrument:
    def __init__(self, 
                 instrument_type='Lockin',
                 address="USB0::0xB506::0x2000::002765::INSTR", 
                 **kwargs
                 ) -> None:
        self.address = address
        if instrument_type == 'Lockin':
            self.additional_channel_num = 2
        elif instrument_type == 'Keithley':
            self.additional_channel_num = 1
        else:
            self.additional_channel_num = 0


class Lockin:
    def __init__(self, scan_parameters, position_parameters, 
                 time_constant_level=0,
                 sample_count=128):

        self.address = scan_parameters.instrument.address
        
        self.sample_count = sample_count
        # self.additional_channel_num = 2
        self.reading_num = position_parameters.x_pixels
        self.time_constant_level = time_constant_level
        # self.initialize_instrument()
    
    # class Trigger():
    #     def __init__(self, instr, reading_num):
    #         self.instr = instr
    #         self.reading_num = reading_num
    #     @contextmanager
    #     def scan(self):
    #         try:
    #             self.instr.write('capturestart one, samp')
    #             yield None
    #         finally:
    #             self.instr.write('capturestop')
    #             buffer_len = int(self.instr.query('captureprog?')[:-1])
    #             self.data = np.array(self.instr.query_binary_values(f'captureget? 0, {buffer_len}')).reshape(-1,2)[:self.reading_num,:].T
         

    @contextmanager
    def initialize_instrument(self):
        try:
            rm = pyvisa.ResourceManager()
            self.instrument = rm.open_resource(self.address)

            # Something happens here

            self.instrument.write('*rst')
            # self.instrument.query('*idn?')
            self.instrument.write(f'oflt {self.time_constant_level}')
            self.instrument.write('capturelen 256')
            self.instrument.write('capturecfg xy')
            self.instrument.write('rtrg posttl')

            yield self.instrument

        finally:
            self.instrument.close()
        
    @contextmanager
    def scan(self, instr):
        try:
            self.instrument.write('capturestart one, samp')
            yield None
        finally:
            self.instrument.write('capturestop')
            buffer_len = int(self.instrument.query('captureprog?')[:-1])
            self.data = np.array(
                self.instrument.query_binary_values(f'captureget? 0, {buffer_len}')
                ).reshape(-1,2)[:self.reading_num,:].T



class Empty_instrument:
    def __init__(self, scan_parameters=None, position_parameters=None):
        self.initialize_instrument()
        self.reading_num = position_parameters.x_pixels
        self.data = np.empty((0, self.reading_num))
    
    @contextmanager
    def initialize_instrument(self):
        try:
            pass
            yield None
        finally:
            pass
        
    @contextmanager
    def scan(self, instr):
        try:
            pass
            yield None
        finally:
            pass


