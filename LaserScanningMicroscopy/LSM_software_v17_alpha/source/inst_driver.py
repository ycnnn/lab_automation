"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np
import numbers
import pyvisa
from contextlib import contextmanager
import warnings
# import Keithley2450_SMU 
from external_instrument_drivers import Keithley2450_SMU as Keithley2450_SMU
# from external_instrument_drivers import K10CR1 as K10CR1
import time

class Instrument:

    def __init__(self, 
                 address, 
                 channel_num, 
                 reading_num, 
                 scan_num,
                 **kwargs):

        self.address = address
        self.channel_num = channel_num
        self.scan_num = scan_num
        self.reading_num = reading_num
        self.data = np.zeros(shape=(self.channel_num, self.reading_num))
        self.params = {}
        self.customized_params = kwargs
        self.params_sweep_lists = {}
    
    def set_up_parameter_list(self):

        for param, _ in self.params.items():
            if param in self.customized_params:
                # Customization
                print(self.__class__.__name__ + ': default parameter overridden: ' + param)
                print(self.__class__.__name__ + ': ' + param + ' set to ' + str(
                    self.customized_params[param]) + '\n')
                param_sweep_list = self.sweep_parameter_generator(
                    param, self.customized_params[param])
                
            else:
                # Using default value
                print(self.__class__.__name__ + ': default parameter used: ' + param)
                print(self.__class__.__name__ + ': ' + param + ' set to ' + str(
                    self.params[param]))
                param_sweep_list = self.sweep_parameter_generator(param, self.params[param] + '\n')
            
            self.params_sweep_lists[param] = param_sweep_list
                
    @contextmanager
    def initialize_and_quit(self, **kwargs):
        try:
            self.initialize(**kwargs)
            yield None
        finally:
            self.quit(**kwargs)
        
    @contextmanager
    def scan(self, **kwargs):
        try:
            self.data_acquisition(**kwargs)
            yield None
        finally:
            pass

    def sweep_parameter_generator(self, param, param_val):

        if isinstance(param_val, numbers.Number):
            # Single input value, the parameter is fixed throughout the scan
            param_sweep_list = param_val * np.ones(shape=(2, self.scan_num))
        elif (isinstance(param_val, tuple) or isinstance(param_val, list)) and len(param_val) == 2:
            # Double input value, the parameter is sweeped from left_val to right_val
            param_sweep_list = np.linspace(
                [param_val[0],param_val[0]],
                [param_val[1],param_val[1]], 
                num=self.scan_num).T
        else:
            # Customizable paraeter sweep list. Must be a np.ndarray
            # Must have shape of (2, self.scan_num); that is, it is made of two 1D array
            # First array defines the sweep list of the trace scan;
            # Second array defines the sweep list of the reverse scan.
            if (not isinstance(param_val, np.ndarray)) or param_val.shape!= (2, self.scan_num):
                raise TypeError('\n\nError when setting up ' + param + ' for ' +  self.__class__.__name__ + ': the user either enetered the wrong parameter format, or indicated customized paramter sweep list, but does not supply a list of correct shape. Acceptable formats: a number, or a tuple of (start_val, end_val), or a numpy array of shape (2, scan_num).')
            param_sweep_list = param_val
        
        return param_sweep_list
    
    # Methods that are instrument-specific
    def initialize(self, **kwargs):
        self.set_up_parameter_list()
        print('Initialized ' + self.__class__.__name__)

    def quit(self, **kwargs):
        print('Initialized ' + self.__class__.__name__)

    def data_acquisition(self, **kwargs):
        total_scan_index = kwargs['total_scan_index']
        self.scan_index = int(total_scan_index/2)
        self.trace_flag = True if total_scan_index % 2 == 0 else False
        trace_sign = 'Trace' if self.trace_flag else 'Retrace'
        print(trace_sign + ': ' + self.__class__.__name__ + f' Scanning at scan_index {self.scan_index}')

class EmptyInstrument(Instrument):
    def __init__(self, address, position_parameters, **kwargs):
        super().__init__(address, channel_num=0, 
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         **kwargs)

    def initialize(self, **kwargs):
        pass

    def quit(self, **kwargs):
        pass

    def data_acquisition(self, **kwargs):
        # scan_index = kwargs['total_scan_index']
        pass
   
class SimulatedInstrument(Instrument):
    def __init__(self, address, position_parameters, **kwargs):
        super().__init__(address, channel_num=1, 
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         **kwargs)
        
        self.params = {'param1':20, 'param2':[0,1], 'param3':0}

    
    def initialize(self, **kwargs):
        super().initialize(**kwargs)

    def quit(self, **kwargs):
        super().quit(**kwargs)

    def data_acquisition(self, **kwargs):
        super().data_acquisition(**kwargs)
        
        
        if self.trace_flag:
            # Trace
            
            self.data = np.random.normal(loc=self.params_sweep_lists['param2'][0,self.scan_index],
                                     size=(self.channel_num, self.reading_num))
        else:
            # Retrace 
            self.data = np.random.normal(loc=self.params_sweep_lists['param2'][1,self.scan_index],
                                     size=(self.channel_num, self.reading_num))

class SMU(Instrument):
    def __init__(self, address, position_parameters, **kwargs):
        super().__init__(address, channel_num=1, 
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         **kwargs)
        
        self.params = {'param1':20, 'param2':[0,1], 'param3':0}

    
    def initialize(self, **kwargs):
        super().initialize(**kwargs)

    def quit(self, **kwargs):
        super().quit(**kwargs)

    def data_acquisition(self, **kwargs):
        super().data_acquisition(**kwargs)
        
        
        if self.trace_flag:
            # Trace
            
            self.data = np.random.normal(loc=self.params_sweep_lists['param2'][0,self.scan_index],
                                     size=(self.channel_num, self.reading_num))
        else:
            # Retrace 
            self.data = np.random.normal(loc=self.params_sweep_lists['param2'][1,self.scan_index],
                                     size=(self.channel_num, self.reading_num))
        
  





































