"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np
import pyvisa
from contextlib import contextmanager
import warnings
import Keithley2450_SMU 
import time

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
                position_parameters,
                **kwargs)
    return instr

class Empty_instrument:
    def __init__(self, scan_parameters=None, position_parameters=None, **kwargs):
        self.initialize_instrument()
        self.reading_num = position_parameters.x_pixels
        self.instrument_params = {}
        self.data = np.empty((0, self.reading_num))
        self.kwargs = kwargs
    
    @contextmanager
    def initialize_instrument(self):
        try:
            for key, value in self.instrument_params.items():
                if key in self.kwargs:
                    self.instrument_params[key] = self.kwargs[key]
                else:
                    warnings.warn('\n\n\nThe ' + key + ' of the instrument is not provided.'
                                +'\nThe ' + key + ' has been set to the default value as ' + str(value) + '.\n\n\n')
            yield None
        finally:
            pass
        
    @contextmanager
    def scan(self, **kwargs):
        try:
            pass
            yield None
        finally:
            pass

class Lockin:
    def __init__(self, scan_parameters, position_parameters, 
                #  sample_count=128,
                 **kwargs):

        self.address = scan_parameters.instrument.address
        
        
        self.reading_num = position_parameters.x_pixels
        self.kwargs = kwargs
        self.instrument_params = {'time_constant_level':5, 'sample_count':128}
 
    @contextmanager
    def initialize_instrument(self):
        try:
            rm = pyvisa.ResourceManager()
            self.instrument = rm.open_resource(self.address)

            # Something happens here
            for key, value in self.instrument_params.items():
                if key in self.kwargs:
                    self.instrument_params[key] = self.kwargs[key]
                else:
                    warnings.warn('\n\n\nThe ' + key + ' of the lockin is not provided.'
                                +'\nThe ' + key + ' has been set to the default value as ' + str(value) + '.\n\n\n')
    
            self.instrument.write('*rst')
            self.instrument.write(f'oflt {self.instrument_params['time_constant_level']}')
            self.instrument.write('capturelen 256')
            self.instrument.write('capturecfg xy')
            self.instrument.write('rtrg posttl')

            yield self.instrument

        finally:
            self.instrument.close()
        
    @contextmanager
    def scan(self, **kwargs):
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
    def __init__(self, scan_parameters=None, position_parameters=None, **kwargs):
        self.initialize_instrument()
        self.reading_num = position_parameters.x_pixels
        self.instrument_params = {}
        self.kwargs = kwargs
        
    
    @contextmanager
    def initialize_instrument(self):
        try:
            for key, value in self.instrument_params.items():
                if key in self.kwargs:
                    self.instrument_params[key] = self.kwargs[key]
                else:
                    warnings.warn('\n\n\nThe ' + key + ' of the instrument is not provided.'
                                +'\nThe ' + key + ' has been set to the default value as ' + str(value) + '.\n\n\n')
            yield None
        finally:
            pass
        
    @contextmanager
    def scan(self, **kwargs):
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
        self.volt_steps = position_parameters.y_pixels
        self.kwargs = kwargs
        self.instrument_params = {'start_volt':0, 'end_volt':0, 'ramp_steps':10}
        for key, value in self.instrument_params.items():
            if key in self.kwargs:
                self.instrument_params[key] = self.kwargs[key]
            else:
                warnings.warn('\n\n\nThe ' + key + ' of the SMU is not provided.'
                              +'\nThe ' + key + ' has been set to the default value as ' + str(value) + '.\n\n\n')
        
        ##################################################################################
        # Instrument-specific initialization
        self.volt_levels = np.repeat(
            np.linspace(self.instrument_params['start_volt'],
                        self.instrument_params['end_volt'],
                        self.volt_steps).reshape(1,-1),
            repeats=2,
            axis=1
        ).reshape(-1)
        
    
    @contextmanager
    def initialize_instrument(self):
        try:
            self.smu = Keithley2450_SMU.set_smu_ready_for_ramp()
            self.smu.write('smu.source.output = smu.ON')
            print('Initialization success')
           
            yield None
        finally:
            Keithley2450_SMU.ramp(
                smu=self.smu)
            self.smu.write('smu.source.output = smu.OFF')
        
    @contextmanager
    def scan(self, **kwargs):
        try:
            scan_index = kwargs['scan_index']
            self.raw_data = Keithley2450_SMU.ramp(
                smu=self.smu, 
                end_volt=self.volt_levels[scan_index])
            print(f'Ramp success @ Step {int(scan_index/2)}')
            # self.data = np.random.random(size=(1, self.reading_num)) * 0.1 + 0.1 * self.volt_levels[scan_index]
            self.data = np.ones(shape=(1, self.reading_num)) * self.raw_data
            yield None
        finally:
            pass
