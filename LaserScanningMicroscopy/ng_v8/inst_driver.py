"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np
import pyvisa
from contextlib import contextmanager
import warnings

instrument_props = {
    'Lockin': {'additional_channel_num':2},
    'Keithley2450': {'additional_channel_num':1},
    'Empty_instrument': {'additional_channel_num':0},
    'Virtual_instrument': {'additional_channel_num':1},
}

class External_instrument:
    def __init__(self, 
                 instrument_type=None,
                 address="USB0::0xB506::0x2000::002765::INSTR", 
                 **kwargs
                 ) -> None:
        self.address = address
        self.instrument_type = instrument_type
        self.additional_channel_num = 0
        self.additional_channel_num = instrument_props[instrument_type]['additional_channel_num']
        self.kwargs = kwargs

def configurate_instrument(instrument,
                          scan_parameters, 
                          position_parameters,
                          **kwargs):
    if instrument.instrument_type == 'Lockin':
        instr = Lockin(scan_parameters, 
                    position_parameters,
                    time_constant_level=5,
                    **kwargs)
                
    elif instrument.instrument_type == 'Virtual_instrument':
        instr = Virtual_instrument(
                scan_parameters, 
                position_parameters,
                **kwargs)     

    elif instrument.instrument_type == 'Keithley2450':
        instr = Keithley2450(
                scan_parameters, 
                position_parameters,
                **kwargs)     
                      
    else:
        instr = Empty_instrument(
                scan_parameters, 
                position_parameters,)
    return instr

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
    def scan(self):
        try:
            pass
            yield None
        finally:
            pass

class Lockin:
    def __init__(self, scan_parameters, position_parameters, 
                #  time_constant_level=0,
                 sample_count=128,
                 **kwargs):

        self.address = scan_parameters.instrument.address
        
        self.sample_count = sample_count
        # self.additional_channel_num = 2
        self.reading_num = position_parameters.x_pixels
        # self.time_constant_level = time_constant_level
        self.kwargs = kwargs
        # self.initialize_instrument()
 
    @contextmanager
    def initialize_instrument(self):
        try:
            rm = pyvisa.ResourceManager()
            self.instrument = rm.open_resource(self.address)

            # Something happens here
            if 'time_constant_level' in self.kwargs:
                self.time_constant_level = self.kwargs['time_constant_level']
            else:
                warnings.warn('\n\n\nThe time constant of the lock-in is not provided.\nThe time constant has been set to the default value as 5.\n\n\n')
                self.time_constant_level = 5

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
    def scan(self):
        try:
            self.instrument.write('capturestart one, samp')
            yield None
        finally:
            self.instrument.write('capturestop')
            buffer_len = int(self.instrument.query('captureprog?')[:-1])
            self.data = np.array(
                self.instrument.query_binary_values(f'captureget? 0, {buffer_len}')
                ).reshape(-1,2)[:self.reading_num,:].T

class Virtual_instrument:
    def __init__(self, scan_parameters=None, position_parameters=None):
        self.initialize_instrument()
        self.reading_num = position_parameters.x_pixels
        
    
    @contextmanager
    def initialize_instrument(self):
        try:
            pass
            yield None
        finally:
            pass
        
    @contextmanager
    def scan(self):
        try:
            pass
            # self.data = np.empty((0, self.reading_num))
            self.data = np.random.random(size=(1, self.reading_num))
            yield None
        finally:
            pass

class Keithley2450:
    def __init__(self, scan_parameters=None, position_parameters=None, **kwargs):
        self.initialize_instrument()
        self.reading_num = position_parameters.x_pixels
        self.kwargs = kwargs
        
    
    @contextmanager
    def initialize_instrument(self):
        try:
            pass
            yield None
        finally:
            pass
        
    @contextmanager
    def scan(self):
        try:
            pass
            if 'val' in self.kwargs:
                self.data = np.random.random(size=(1, self.reading_num)) * 0.1 + self.kwargs['val']
            else:
                warnings.warn('\n\n\nThe VAL of the SMU is not provided.\nThe VAL has been set to the default value as 0.\n\n\n')
                self.data = np.random.random(size=(1, self.reading_num)) * 0.1
            yield None
        finally:
            pass
