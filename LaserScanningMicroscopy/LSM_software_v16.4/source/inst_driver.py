"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np
import pyvisa
from contextlib import contextmanager
import warnings
# import Keithley2450_SMU 
from external_instrument_drivers import Keithley2450_SMU as Keithley2450_SMU
import time

instrument_props = {
    'DAQ': {'additional_channel_num':1},
    'Lockin': {'additional_channel_num':2},
    'Keithley2450': {'additional_channel_num':1},
    'Empty_instrument': {'additional_channel_num':0},
    'Virtual_instrument': {'additional_channel_num':1},
    'Laser':{'additional_channel_num':0}
}

def parameter_list_generator(start_val, end_val, position_parameters):
    parameter_levels = np.repeat(
            np.linspace(start_val,
                        end_val,
                        position_parameters.y_pixels).reshape(1,-1),
            repeats=2,
            axis=1
        ).reshape(-1)
    return parameter_levels

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
    elif instrument.instrument_type == 'Laser':
        instr = LaserDiode(
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
        
        self.reading_num = position_parameters.x_pixels
        self.instrument_params = {}
        self.data = np.empty((0, self.reading_num))
        self.kwargs = kwargs

        for key, value in self.instrument_params.items():
            if key in self.kwargs:
                self.instrument_params[key] = self.kwargs[key]
            else:
                warnings.warn('\n\n\nThe ' + key + ' of the instrument is not provided.'
                                +'\nThe ' + key + ' has been set to the default value as ' + str(value) + '.\n\n\n')
        
    
    @contextmanager
    def initialize_instrument(self):
        try:
            # for key, value in self.instrument_params.items():
            #     if key in self.kwargs:
            #         self.instrument_params[key] = self.kwargs[key]
            #     else:
            #         warnings.warn('\n\n\nThe ' + key + ' of the instrument is not provided.'
            #                     +'\nThe ' + key + ' has been set to the default value as ' + str(value) + '.\n\n\n')
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

        
        self.reading_num = position_parameters.x_pixels
        self.kwargs = kwargs
        self.instrument_params = {'address': "USB0::0xB506::0x2000::002765::INSTR",
                                  'time_constant_level':9, 
                                  'volt_input_range':2, 
                                  'signal_sensitivity':6,
                                  'ref_frequency':20170,
                                  'start_sine_amplitude':0.5,
                                  'end_sine_amplitude':0.5
                                  }
        
        for key, value in self.instrument_params.items():
            if key in self.kwargs:
                self.instrument_params[key] = self.kwargs[key]
            else:
                warnings.warn('\n\n\nThe ' + key + ' of the lockin is not provided.'
                                +'\nThe ' + key + ' has been set to the default value as ' + str(value) + '.\n\n\n')
        # self.sine_amplitudes = np.linspace(self.instrument_params['start_sine_amplitude'],
        #                                    self.instrument_params['end_sine_amplitude'],
        #                                    num=position_parameters.y_pixels)
        self.sine_amplitudes = parameter_list_generator(start_val=self.instrument_params['start_sine_amplitude'],
                                                    end_val=self.instrument_params['end_sine_amplitude'],
                                                    position_parameters=position_parameters)
    
 
    @contextmanager
    def initialize_instrument(self):

        try:
            rm = pyvisa.ResourceManager()
            self.instrument = rm.open_resource(self.instrument_params['address'])

            # Reset
            self.instrument.write('*rst')
            self.instrument.query('*idn?')

            # build buffer
            self.instrument.write('capturelen 256')

            # record XY signals
            self.instrument.write('capturecfg xy')

            # Set the capture mode as external trigger
            self.instrument.write('rtrg posttl')

            # Set the input source as VOLTAGE
            self.instrument.write('ivmd volt')
            self.instrument.query('ivmd?')

            # Set the input mode as A
            self.instrument.write('isrc 0')
            self.instrument.query('isrc?')

            # Set the input coupling. Always use AC coupling unless signal frequency <= 0.16 Hz (unlikely)
            self.instrument.write('icpl 0')
            self.instrument.query('icpl?')

            # Set the voltage input shield as float
            self.instrument.write('ignd 0')
            self.instrument.query('ignd?')

            # Set the voltage input range
            # Levels and range: 0->1V, 1->300mV, 2->100mV 3->30mV, 4->10mV
            self.instrument.write(f"irng {self.instrument_params['volt_input_range']}")
            self.instrument.query('irng?')

            # Set the signal sensitivity
            # Levels and range: 0->1V, 1->500mV, 2->200mV 3->100mV, 4->50mV, 5->20mV, 6->10mV, 7->5mV, 8->2mV, 
            # 9->1mV, 10->500uV, 11->200uV, 12->100uV, 13->50uV, 14->20uV
            self.instrument.write(f"scal {self.instrument_params['signal_sensitivity']}")
            self.instrument.query('scal?')

            # Set the time constant
            # Levels and range: 0->1us, 1->3us, 2->10us 3->30us, 4->100us, 5->300us, 6->1ms, 7->3ms, 8->10ms, 
            # 9->30ms, 10->100ms, 11->300ms, 12->1s, 13->3s, 14->10s, 15->30s, 16->100s, 17->300s, 18->1000s, 19->3000s, 20->10000s
            self.instrument.write(f"oflt {self.instrument_params['time_constant_level']}")
            self.instrument.query('oflt?')

            # Set the reference frequency of the sine output signal as 20.17 kHz
            self.instrument.write(f"freq {self.instrument_params['ref_frequency']}")
            self.instrument.query('freq?')

            # Set the amplitude of the sine output signal 
            self.instrument.write(f"slvl {self.sine_amplitudes[0]}")
            self.instrument.query('slvl?')


            yield self.instrument

        finally:
            # Turn off sine output
            self.instrument.write(f"slvl 0")
            self.instrument.query('slvl?')
            # Disconnect 
            self.instrument.close()
        
    @contextmanager
    def scan(self, **kwargs):
        try:
            scan_index = kwargs['scan_index']
            self.instrument.write(f"slvl {self.sine_amplitudes[scan_index]}")
            self.instrument.write('capturestart one, samp')
            yield None
        finally:
            self.instrument.write('capturestop')
            buffer_len = int(self.instrument.query('captureprog?')[:-1])
            input_data = np.array(
                self.instrument.query_binary_values(f'captureget? 0, {buffer_len}')
                ).reshape(-1,2)[:self.reading_num,:].T
            # self.data = np.flip(input_data, axis=1)
            self.data = input_data

class Virtual_instrument:
    def __init__(self, scan_parameters=None, position_parameters=None, **kwargs):
        self.initialize_instrument()
        self.reading_num = position_parameters.x_pixels
        self.instrument_params = {}
        self.kwargs = kwargs

        for key, value in self.instrument_params.items():
            if key in self.kwargs:
                self.instrument_params[key] = self.kwargs[key]
            else:
                warnings.warn('\n\n\nThe ' + key + ' of the instrument is not provided.'
                            +'\nThe ' + key + ' has been set to the default value as ' + str(value) + '.\n\n\n')
    
    
    @contextmanager
    def initialize_instrument(self):
        try:
            # for key, value in self.instrument_params.items():
            #     if key in self.kwargs:
            #         self.instrument_params[key] = self.kwargs[key]
            #     else:
            #         warnings.warn('\n\n\nThe ' + key + ' of the instrument is not provided.'
            #                     +'\nThe ' + key + ' has been set to the default value as ' + str(value) + '.\n\n\n')
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
        
        self.reading_num = position_parameters.x_pixels
        self.volt_steps = position_parameters.y_pixels
        self.kwargs = kwargs
        self.instrument_params = {'start_volt':0, 
                                  'end_volt':0, 
                                  'ramp_steps':10,
                                  'address':"USB0::0x05E6::0x2450::04096331::INSTR"}
        for key, value in self.instrument_params.items():
            if key in self.kwargs:
                self.instrument_params[key] = self.kwargs[key]
            else:
                warnings.warn('\n\n\nThe ' + key + ' of the SMU is not provided.'
                              +'\nThe ' + key + ' has been set to the default value as ' + str(value) + '.\n\n\n')
        
        ##################################################################################
        # Instrument-specific initialization
        # self.volt_levels = np.repeat(
        #     np.linspace(self.instrument_params['start_volt'],
        #                 self.instrument_params['end_volt'],
        #                 self.volt_steps).reshape(1,-1),
        #     repeats=2,
        #     axis=1
        # ).reshape(-1)
        self.volt_levels = parameter_list_generator(start_val=self.instrument_params['start_volt'],
                                                    end_val=self.instrument_params['end_volt'],
                                                    position_parameters=position_parameters)

        # self.initialize_instrument()
        
    
    @contextmanager
    def initialize_instrument(self):
        try:
            self.smu = Keithley2450_SMU.set_smu_ready_for_ramp(address=self.instrument_params['address'])
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



class LaserDiode:
    def __init__(self, scan_parameters=None, position_parameters=None, **kwargs):
        self.initialize_instrument()
        self.reading_num = position_parameters.x_pixels
        self.data = np.empty((0, self.reading_num))
        self.instrument_params = {'address':'USB0::0x1313::0x804F::M00332686::INSTR',
                                  'start_current_level':0.080,
                                  'end_current_level':0.080}
        self.kwargs = kwargs


        for key, value in self.instrument_params.items():
            if key in self.kwargs:
                self.instrument_params[key] = self.kwargs[key]
            else:
                warnings.warn('\n\n\nThe ' + key + ' of the instrument is not provided.'
                            +'\nThe ' + key + ' has been set to the default value as ' + str(value) + '.\n\n\n')
                
        # self.current_levels = np.linspace(self.instrument_params['start_current_level'],
        #                                    self.instrument_params['end_current_level'],
        #                                    num=position_parameters.y_pixels)
        self.current_levels = parameter_list_generator(start_val=self.instrument_params['start_current_level'],
                                                    end_val=self.instrument_params['end_current_level'],
                                                    position_parameters=position_parameters)
    
    
    @contextmanager
    def initialize_instrument(self):
        try:
            rm = pyvisa.ResourceManager()
            self.instrument = rm.open_resource(self.instrument_params['address'])
            # self.instrument.write('*rst')
            if np.min(self.current_levels) < 0 or np.max(self.current_levels) >= 0.101:
                print('Warning: the laser current setpoint is outside the allowed range.\nFor your safety, the laser power has been set to 10 mA.')
                self.current_levels = 0.01 * np.ones(self.current_levels.shape) 
            self.instrument.write(f"source1:current:level:amplitude {self.current_levels[0]}")
            self.instrument.write('output:state 1')
            yield None
        finally:
            self.instrument.write('output:state 0')
            self.instrument.write(f"source1:current:level:amplitude 0.01")
            self.instrument.close()
        
    @contextmanager
    def scan(self, **kwargs):
        try:
            scan_index = kwargs['scan_index']
            self.instrument.write(f"source1:current:level:amplitude {self.current_levels[scan_index]}")
            yield None
        finally:
            pass
