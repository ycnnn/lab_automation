"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np
import numbers
import os
import pyvisa
from contextlib import contextmanager
import warnings
# from pathlib import Path

import time
import nidaqmx as ni
from nidaqmx.constants import WAIT_INFINITELY
from nidaqmx.constants import Edge, AcquisitionType, TaskMode, WAIT_INFINITELY
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter

from nidaqmx.system import System as nidaqSystem
# from source.logger import Logger
# from source.daq_driver import daq_interface, reset_daq


class Instrument:

    # log_file_path = os.path.dirname(os.path.dirname(__file__)) + '/temp_files/temp_instr_log.txt'
    # logger = Logger(log_file_path)

    def __init__(self, 
                 address, 
                 channel_num, 
                 reading_num, 
                 scan_num,
                 name=None,
                 channel_name_list=None,
                 **kwargs):
        
        self.name = self.__class__.__name__ if not name else name
        self.address = address


        # self.logger = Logger(os.path.dirname(os.path.realpath(__file__)) + '/')
        self.channel_num = channel_num

        # self.channel_name_list stores the name for each channel. 
        # It has to be of size self.channel_num.
        # If user doesn't supply it, then it will be automatically generated 
        # Channel name list will ONLY be used to name the channels for collected data, 
        # so it is not necessary to create a channel name list for instruments with 0 channel 
        # (i.e., does not collect or acquisit data).
      
        self.channel_name_list = []
        for chan_id in range(self.channel_num):
            if channel_name_list:
                self.channel_name_list.append(self.name + '_' + channel_name_list[chan_id])
            else:
                self.channel_name_list.append(self.name + f'_ch_{chan_id}')


        self.scan_num = scan_num
        self.reading_num = reading_num
        self.data = np.zeros(shape=(self.channel_num, self.reading_num))
        # self.params stores the default parameter setting for the instrument
        self.params = {}
        # self.customized_params are the customized parameter setting 
        # for the instrument from the user
        self.customized_params = kwargs
        # self.params_sweep_lists stores the instrument parameter for each trace and retrace step
        self.params_sweep_lists = {}
        # self.params_state stores the lasest snapshot of the instrument parameter, 
        # e.g., parameters used for the last scan
        self.params_state = {}
        # self.params_config_save stores the parameter configuration that is actuall used in this scan. 
        # It will be saved as a json file for future reference.
        self.params_config_save = {}
    
    def set_up_parameter_list(self):

        for param, _ in self.params.items():
            # Set up initial parameters sanpshot
            self.params_state[param] = None
            if param in self.customized_params:
                # Customization
                self.logger.info(self.name + ': default parameter overridden: ' + param)
                self.logger.info(self.name + ': ' + param + ' set to ' + str(
                    self.customized_params[param]) + '\n')
                if isinstance(self.customized_params[param], np.ndarray):
                    self.params_config_save[param]= self.customized_params[param].tolist()   
                else: 
                    self.params_config_save[param]= self.customized_params[param]    
                param_sweep_list = self.sweep_parameter_generator(
                    param, self.customized_params[param])
                
                
            else:
                # Using default value
                self.logger.info(self.name + ': default parameter used: ' + param)
                self.logger.info(self.name + ': ' + param + ' set to ' + str(
                    self.params[param]))
                self.params_config_save[param]= self.params[param]
                param_sweep_list = self.sweep_parameter_generator(param, self.params[param])
            
            self.params_sweep_lists[param] = param_sweep_list


    @contextmanager
    def initialize_and_quit(self, **kwargs):
        try:
            self.logger = kwargs['logger']
            self.initialize(**kwargs)
            yield None
        finally:
            self.quit(**kwargs)
        
    @contextmanager
    def scan(self, **kwargs):
        try:
            self.data_acquisition_start(**kwargs)
            yield None
        finally:
            self.data_acquisition_finish(**kwargs)

    def sweep_parameter_generator(self, param, param_val):

        if isinstance(param_val, numbers.Number):
            # Single input value, the parameter is fixed throughout the scan
            param_sweep_list = param_val * np.ones(shape=(2, self.scan_num))
        elif isinstance(param_val, list) and len(param_val) == 2:
            # Double input value, 
            # If input is of format [start, end], the parameter is sweeped from left_val to right_val
            # If input is of format [[trace_val], [retrace_val]], the trace scan will use trace_val, and the retrace scan will use retrace_val
            param_val_in_ndarray = np.array(param_val)

            if param_val_in_ndarray.shape == (2,):
                param_sweep_list = np.linspace(
                [param_val_in_ndarray[0],param_val_in_ndarray[0]],
                [param_val_in_ndarray[1],param_val_in_ndarray[1]], 
                num=self.scan_num).T
            elif param_val_in_ndarray.shape == (2,1):
                param_sweep_list = np.linspace(
                [param_val_in_ndarray[0,0],param_val_in_ndarray[1,0]],
                [param_val_in_ndarray[0,0],param_val_in_ndarray[1,0]], 
                num=self.scan_num).T
        else:
            # Customizable paraeter sweep list. Must be a np.ndarray
            # Must have shape of (2, self.scan_num); that is, it is made of two 1D array
            # First array defines the sweep list of the trace scan;
            # Second array defines the sweep list of the reverse scan.
            if (not isinstance(param_val, np.ndarray)) or param_val.shape!= (2, self.scan_num):
                error_message = '\n\nError when setting up ' + param + ' for ' +  self.name + ': the user either enetered the wrong parameter format, or indicated customized paramter sweep list, but does not supply a list of correct shape. Acceptable formats: a number, or a tuple of (start_val, end_val), or a numpy array of shape (2, scan_num).'
                self.logger.info(error_message)
                raise TypeError(error_message)
            param_sweep_list = param_val
        
        return param_sweep_list
    def initialize_visa_type_instrument(self):
        rm = pyvisa.ResourceManager()
        self.logger.info('\n\nInitializing...\n\n')
        self.instrument = rm.open_resource(self.address)
        if not self.instrument:
            error_message = f'Instrument {self.name} has not been initialized successfuly. Check if it has been turned on, and the address {self.address} is correct.'
            raise RuntimeError(error_message)
    # Methods that are instrument-specific
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################

    def initialize(self, **kwargs):
        self.set_up_parameter_list()
        self.logger.info('Initialized ' + self.name)
   

    def quit(self, **kwargs):
        try:
            self.instrument.close()
        except:
            pass
        self.logger.info('Quitted ' + self.name)
        # os.remove(self.log_file_path)

    def write_param_to_instrument(self, param, target_val):
        return None

    def data_acquisition_start(self, **kwargs):
        self.total_scan_index = kwargs['total_scan_index']
        self.scan_index = int(self.total_scan_index/2)
        self.trace_flag = True if self.total_scan_index % 2 == 0 else False
        self.trace_id = 0 if self.total_scan_index % 2 == 0 else 1
        trace_sign = 'Trace' if self.trace_flag else 'Retrace'
        self.logger.info(trace_sign + ': ' + self.name + f' Scanning at scan_index {self.scan_index}')
        ramp_data = {}

        for param, param_sweep_list in self.params_sweep_lists.items():
            target_val = param_sweep_list[self.trace_id,self.scan_index]

            ramp_data[param] = self.write_param_to_instrument(param, target_val)
            self.logger.info(f'At ' + trace_sign + f' scan {self.scan_index}, ' + param + ' for ' + self.name + f' set to {target_val}.')
     
            self.params_state[param] = target_val


        
        return ramp_data
    
    def data_acquisition_finish(self, **kwargs):
        return None

        # for param, param_sweep_list in self.params_sweep_lists.items():
        #     target_val = param_sweep_list[self.trace_id,self.scan_index]
        #     if target_val != self.params_state[param]:
        #         self.write_param_to_instrument(param, target_val)
        #         self.logger.info(f'At ' + trace_sign + f' scan {self.scan_index}, ' + param + ' for ' + self.name + f' set to {target_val}.')
        #     else:
        #         self.logger.info(f'At ' + trace_sign + f' scan {self.scan_index}, writing ' + param + ' for ' + self.name +' skipped because no change in its set value.')
        #     self.params_state[param] = target_val

class EmptyInstrument(Instrument):
    def __init__(self, address, position_parameters, **kwargs):
        super().__init__(address, channel_num=0, 
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         **kwargs)

    def initialize(self, **kwargs):
        super().initialize(**kwargs)
  

    def quit(self, **kwargs):
        super().quit(**kwargs)


    def data_acquisition_start(self, **kwargs):
        # scan_index = kwargs['total_scan_index']
        pass
   
class SimulatedInstrument(Instrument):
    def __init__(self, address, position_parameters, name=None,**kwargs):
        super().__init__(address, channel_num=1, 
                         name=name,
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         channel_name_list=['Sim_instr'],
                         **kwargs)
        
     

        self.params = {'param1':20, 'param2':1, 'param3':0}
        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)

    def quit(self, **kwargs):
        super().quit(**kwargs)

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)

    def data_acquisition_start(self, **kwargs):
        ramp_data = super().data_acquisition_start(**kwargs)


        self.data = np.random.normal(
                loc=self.params_sweep_lists['param2'][self.trace_id,self.scan_index],
                size=(self.channel_num, self.reading_num))

class SMU_deprecated(Instrument):
    def __init__(self, position_parameters, 
                 address="USB0::0x05E6::0x2450::04096331::INSTR",
                 name=None,
                 ramp_steps=10,
                 **kwargs):
        
        super().__init__(address, channel_num=1, 
                         name=name,
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         channel_name_list=['Voltage'],
                         **kwargs)
        
        
        self.ramp_steps = ramp_steps
        self.params = {'voltage':0}

        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        self.initialize_visa_type_instrument()
        self.smu.timeout = 500
        self.smu.write('reset()')
        self.smu.write("smu.source.autorange = smu.ON")
        self.smu.write("smu.measure.func = smu.FUNC_DC_VOLTAGE")
        self.smu.write("smu.measure.autorange = smu.ON")
        self.smu.write("smu.measure.terminals = smu.TERMINALS_FRONT")
        self.smu.write("smu.measure.func = smu.FUNC_DC_VOLTAGE")
        self.smu.write("smu.source.level = 0")
        self.smu.write('smu.source.output = smu.ON')


    def quit(self, **kwargs):
        
        self.write_param_to_instrument('voltage', 0)
        self.smu.write('smu.source.output = smu.OFF')
        super().quit(**kwargs)

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)
    # By default, ramp Keithley 2450 SMU from current voltage level to the target voltage level (end_volt).
        ramp_steps=self.ramp_steps
        self.smu.write('reading = smu.measure.read()')
        volt_reading = np.array(self.smu.query_ascii_values('print(reading)'))[0]
        self.logger.info(f'Current VOLT reading is {volt_reading} V.')
        start_volt = volt_reading
        end_volt = param_val
        voltages = np.linspace(start_volt, end_volt, ramp_steps)
        volt_readings = []
        # return start_volt
        for volt in voltages:
            self.smu.write(f"smu.source.level = {volt}")
            self.smu.write('reading = smu.measure.read()')
            volt_reading = self.smu.query_ascii_values('print(reading)')
            self.smu.write('waitcomplete()')
            volt_readings.append(volt_reading)

        return np.array(volt_readings).reshape(-1)[-1]

    def data_acquisition_start(self, **kwargs):
        ramp_data = super().data_acquisition_start(**kwargs)
        measured_voltage = ramp_data['voltage']
        self.data = np.ones(shape=(self.channel_num, self.reading_num)) * measured_voltage
        

class SMU(Instrument):
    def __init__(self, position_parameters, 
                 address="USB0::0x05E6::0x2450::04096331::INSTR",
                 name=None,
                 ramp_steps=10,
                 **kwargs):
       

        super().__init__(address, channel_num=1, 
                         name=name,
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         channel_name_list=['Voltage'],
                         **kwargs)
        self.ramp_steps = ramp_steps
        self.params = {'voltage':0}
        
        
        
        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        self.initialize_visa_type_instrument()
        self.instrument.timeout = 500
        self.instrument.write('reset()')
        self.instrument.write("smu.source.autorange = smu.ON")
        self.instrument.write("smu.measure.func = smu.FUNC_DC_VOLTAGE")
        self.instrument.write("smu.measure.autorange = smu.ON")
        self.instrument.write("smu.measure.terminals = smu.TERMINALS_FRONT")
        self.instrument.write("smu.measure.func = smu.FUNC_DC_VOLTAGE")
        self.instrument.write("smu.source.level = 0")
        self.instrument.write('smu.source.output = smu.ON')


    def quit(self, **kwargs):
        self.write_param_to_instrument('voltage', 0)
        self.instrument.write('smu.source.output = smu.OFF')
        super().quit(**kwargs)

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)
    # By default, ramp Keithley 2450 SMU from current voltage level to the target voltage level (end_volt).
        ramp_steps=self.ramp_steps
        # In some cases, the SMU will not be able to measure the voltage and report the result timely.
        # An easy fix is to ask the SMU to measure and report again.
        try:
            volt_reading = np.array(self.instrument.query_ascii_values('print(smu.measure.read())'))[0]
        except:
            self.logger.info('The SMU ' + self.name + ' fails to read its source output value. Try again.')
            volt_reading = np.array(self.instrument.query_ascii_values('print(smu.measure.read())'))[0]
        
        self.logger.info(f'Current VOLT reading is {volt_reading} V.')
        start_volt = volt_reading
        end_volt = param_val
        voltages = np.linspace(start_volt, end_volt, ramp_steps)
        volt_readings = []
        # return start_volt
        for volt in voltages:
            self.instrument.write(f"smu.source.level = {volt}")
            # self.instrument.write('reading = smu.measure.read()')
            try:
                volt_reading = self.instrument.query_ascii_values('print(smu.measure.read())')
            except:
                self.logger.info('The SMU ' + self.name + ' fails to read its source output value. Try again.')
                volt_reading = self.instrument.query_ascii_values('print(smu.measure.read())')
            self.instrument.write('waitcomplete()')
            volt_readings.append(volt_reading)

        return np.array(volt_readings).reshape(-1)[-1]

    def data_acquisition_start(self, **kwargs):
        ramp_data = super().data_acquisition_start(**kwargs)
        measured_voltage = ramp_data['voltage']
        self.data = np.ones(shape=(self.channel_num, self.reading_num)) * measured_voltage
        


class Lockin(Instrument):
    def __init__(self, 
                 address="USB0::0xB506::0x2000::002765::INSTR", 
                 position_parameters=None, 
                 name=None, 
                 **kwargs):
        super().__init__(address, channel_num=2, 
                         name=name,
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         channel_name_list = ['X', 'Y'],
                         **kwargs)
        
    

        self.params = {'time_constant_level':8, 
                        'volt_input_range':3, 
                        'signal_sensitivity':12,
                                  }
        
        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)

        self.initialize_visa_type_instrument()

        # Reset
        self.instrument.write('*rst')
        # self.logger.info(self.instrument.query('*idn?'))

        # build buffer
        self.instrument.write('capturelen 256')

        # record XY signals
        self.instrument.write('capturecfg xy')

        # Set the capture mode as external trigger
        self.instrument.write('rtrg posttl')

        # Set the input source as VOLTAGE
        self.instrument.write('ivmd volt')
        # self.logger.info(self.instrument.query('ivmd?'))

        # Set the input mode as A
        self.instrument.write('isrc 0')
        # self.logger.info(self.instrument.query('isrc?'))

        # Set the input coupling. Always use AC coupling unless signal frequency <= 0.16 Hz (unlikely)
        self.instrument.write('icpl 0')
        # self.logger.info(self.instrument.query('icpl?'))

        # Set the voltage input shield as float
        self.instrument.write('ignd 0')
        # self.logger.info(self.instrument.query('ignd?'))

        # Set the voltage input range
        # Levels and range: 0->1V, 1->300mV, 2->100mV 3->30mV, 4->10mV
        self.instrument.write(f"irng {self.params_sweep_lists['volt_input_range'][0,0]}")
        # self.logger.info(self.instrument.query('irng?'))

        # Set the signal sensitivity
        # Levels and range: 0->1V, 1->500mV, 2->200mV 3->100mV, 4->50mV, 5->20mV, 6->10mV, 7->5mV, 8->2mV, 
        # 9->1mV, 10->500uV, 11->200uV, 12->100uV, 13->50uV, 14->20uV
        self.instrument.write(f"scal {self.params_sweep_lists['signal_sensitivity'][0,0]}")
        # self.logger.info(self.instrument.query('scal?'))

        # Set the time constant
        # Levels and range: 0->1us, 1->3us, 2->10us 3->30us, 4->100us, 5->300us, 6->1ms, 7->3ms, 8->10ms, 
        # 9->30ms, 10->100ms, 11->300ms, 12->1s, 13->3s, 14->10s, 15->30s, 16->100s, 17->300s, 18->1000s, 19->3000s, 20->10000s
        self.instrument.write(f"oflt {self.params_sweep_lists['time_constant_level'][0,0]}")
        # self.logger.info(self.instrument.query('oflt?'))

        # Set the reference mode as external reference
        self.instrument.write(f"rsrc 1")
        # Set the external reference trigger mode as positive TTL
        self.instrument.write(f"rtrg 1")
        # Set the external reference trigger input to 1 MOhm
        self.instrument.write(f"refz 1")


    def quit(self, **kwargs):
        # Turn off sine output
        # Disconnect 
        super().quit(**kwargs)

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)

        if self.params_state[param] == param_val:
            self.logger.info('Writing ' + param + f' at level {param_val} skipped, because there is no change in the set value.' )
            return None

        if param == 'time_constant_level':
            self.instrument.write(f"oflt {param_val}")
        elif param == 'volt_input_range':
            self.instrument.write(f"irng {param_val}")
        elif param == 'signal_sensitivity':
            self.instrument.write(f"scal {param_val}")

        return None

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)

        self.instrument.write('capturestart one, samp')


  
    
    def data_acquisition_finish(self, **kwargs):
        super().data_acquisition_finish(**kwargs)

        self.instrument.write('capturestop')
        buffer_len = int(self.instrument.query('captureprog?')[:-1])
        input_data = np.array(
            self.instrument.query_binary_values(f'captureget? 0, {buffer_len}')
            ).reshape(-1,2)[:self.reading_num,:].T


        self.data = input_data      
  


class Lockin_dual_freq(Instrument):
    def __init__(self, 
                 address="USB0::0xB506::0x2000::002765::INSTR", 
                 position_parameters=None, 
                 name=None, 
                 **kwargs):
        super().__init__(address, channel_num=2, 
                         name=name,
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         channel_name_list = ['X', 'Y'],
                         **kwargs)
        
       

        self.params = {'time_constant_level':8, 
                        'volt_input_range':3, 
                        'signal_sensitivity':12,
                        'internal_frequency':10170,
                        'internal_sine_amplitude':0.50,
                                  }
        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)

        self.initialize_visa_type_instrument()

        # Reset
        self.instrument.write('*rst')
        # self.logger.info(self.instrument.query('*idn?'))

        # build buffer
        self.instrument.write('capturelen 256')

        # record XY signals
        self.instrument.write('capturecfg xy')

        # Set the capture mode as external trigger
        self.instrument.write('rtrg posttl')

        # Set the input source as VOLTAGE
        self.instrument.write('ivmd volt')
        # self.logger.info(self.instrument.query('ivmd?'))

        # Set the input mode as A
        self.instrument.write('isrc 0')
        # self.logger.info(self.instrument.query('isrc?'))

        # Set the input coupling. Always use AC coupling unless signal frequency <= 0.16 Hz (unlikely)
        self.instrument.write('icpl 0')
        # self.logger.info(self.instrument.query('icpl?'))

        # Set the voltage input shield as float
        self.instrument.write('ignd 0')
        # self.logger.info(self.instrument.query('ignd?'))

        # Set the voltage input range
        # Levels and range: 0->1V, 1->300mV, 2->100mV 3->30mV, 4->10mV
        self.instrument.write(f"irng {self.params_sweep_lists['volt_input_range'][0,0]}")
        # self.logger.info(self.instrument.query('irng?'))

        # Set the internal reference frequency
        self.instrument.write(f"freq {self.params_sweep_lists['internal_frequency'][0,0]}")
        # Set the initernal reference outout amplitude
        self.instrument.write(f"slvl {self.params_sweep_lists['internal_sine_amplitude'][0,0]}")

        
        # Set the signal sensitivity
        # Levels and range: 0->1V, 1->500mV, 2->200mV 3->100mV, 4->50mV, 5->20mV, 6->10mV, 7->5mV, 8->2mV, 
        # 9->1mV, 10->500uV, 11->200uV, 12->100uV, 13->50uV, 14->20uV
        self.instrument.write(f"scal {self.params_sweep_lists['signal_sensitivity'][0,0]}")
        # self.logger.info(self.instrument.query('scal?'))

        # Set the time constant
        # Levels and range: 0->1us, 1->3us, 2->10us 3->30us, 4->100us, 5->300us, 6->1ms, 7->3ms, 8->10ms, 
        # 9->30ms, 10->100ms, 11->300ms, 12->1s, 13->3s, 14->10s, 15->30s, 16->100s, 17->300s, 18->1000s, 19->3000s, 20->10000s
        self.instrument.write(f"oflt {self.params_sweep_lists['time_constant_level'][0,0]}")
        # self.logger.info(self.instrument.query('oflt?'))

        # Set the reference mode as external reference
        self.instrument.write(f"rsrc 2")
        # Set the external reference trigger mode as positive TTL
        self.instrument.write(f"rtrg 1")
        # Set the external reference trigger input to 1 MOhm
        self.instrument.write(f"refz 1")


    def quit(self, **kwargs):
        # Turn off sine output
        self.instrument.write(f"slvl 0")
        # Disconnect 
        super().quit(**kwargs)

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)

        if self.params_state[param] == param_val:
            self.logger.info('Writing ' + param + f' at level {param_val} skipped, because there is no change in the set value.' )
            return None

        if param == 'time_constant_level':
            self.instrument.write(f"oflt {param_val}")
        elif param == 'volt_input_range':
            self.instrument.write(f"irng {param_val}")
        elif param == 'signal_sensitivity':
            self.instrument.write(f"scal {param_val}")
        elif param == 'internal_frequency':
            self.instrument.write(f"freq {param_val}")
        elif param == 'internal_sine_amplitude':
            self.instrument.write(f"slvl {param_val}")

    

        return None

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)

        self.instrument.write('capturestart one, samp')


  
    
    def data_acquisition_finish(self, **kwargs):
        super().data_acquisition_finish(**kwargs)

        self.instrument.write('capturestop')
        buffer_len = int(self.instrument.query('captureprog?')[:-1])
        input_data = np.array(
            self.instrument.query_binary_values(f'captureget? 0, {buffer_len}')
            ).reshape(-1,2)[:self.reading_num,:].T

        self.data = input_data      
  

class LaserDiode(Instrument):
    def __init__(self, address='USB0::0x1313::0x804F::M00332686::INSTR', 
                 position_parameters=None, 
                 name=None, 
                 **kwargs):
        
        super().__init__(address, channel_num=0, 
                         name=name,
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         **kwargs)
        
     

        self.params = {'current':0.00}
        
        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        self.initialize_visa_type_instrument()
   
        if np.min(
            self.params_sweep_lists['current']
            ) < 0 or np.max(
            self.params_sweep_lists['current']
            ) >= 0.035:
            self.logger.info('Warning: the laser current setpoint is outside the allowed range.\nFor your safety, the laser power has been set to 10 mA.')
            self.current_levels = np.zeros(self.params_sweep_lists['current'].shape)

        # self.instrument.write(f"source1:current:level:amplitude {self.params_sweep_lists['current'][0,0]}")
        self.instrument.write(f"source1:current:level:amplitude 0")
        self.instrument.write('output:state 1')

    def quit(self, **kwargs):
        
        # self.instrument.write('output:state 0')
        self.instrument.write(f"source1:current:level:amplitude 0")
        super().quit(**kwargs)

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)
        if param_val == self.params_state[param]:
            self.logger.info('Writing ' + param + ' for ' + self.name + ' skipped, because there is no change in the set value.')
            return None
        self.instrument.write(f"source1:current:level:amplitude {param_val}")

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)
        # if self.total_scan_index == 0:
        #     self.instrument.write('output:state 1')

    def data_acquisition_finish(self, **kwargs):
        super().data_acquisition_finish(**kwargs)
        # if self.total_scan_index >= 2 * self.scan_num - 1:
        #     self.instrument.write('output:state 0')

class Oscilloscope(Instrument):
    def __init__(self, address='USB0::0x0957::0x179A::MY51350123::INSTR', 
                 position_parameters=None, 
                 name=None, 
                 **kwargs):
        
        super().__init__(address, channel_num=0, 
                         name=name,
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         **kwargs)
        
 

        self.params = {'chopper_frequency':810.0,
                       'duty_cycle_percent': 50,
                       'mod_volt_high_in_volt':0.17,
                       'mod_volt_low_in_volt':0.0}
        
        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        self.initialize_visa_type_instrument()

        self.logger.info('Currently, the oscilloscope does not support variable input parameters.')
   
        if np.min(
            self.params_sweep_lists['mod_volt_high_in_volt']
            ) < 0 or np.max(
            self.params_sweep_lists['mod_volt_high_in_volt']
            ) >= 0.30:
            self.logger.info('Error: the modulated laser current setpoint is outside the allowed range.\nCheck the mod voltage high level. Laser current = 150 mA/V * modulation voltage.')
            raise RuntimeError('Error: the modulated laser current setpoint is outside the allowed range.\nCheck the mod voltage high level. Laser current = 150 mA/V * modulation voltage.')

        # Set the wave generator output as square wave
        self.instrument.write(':wgen:func squ')
        # Set the rear BNC output as synchronized TTL signal
        self.instrument.write(':cal:outp wave')
   
    def quit(self, **kwargs):

        self.instrument.write(':wgen:outp 0')
        super().quit(**kwargs)

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)
        if param_val == self.params_state[param]:
            self.logger.info('Writing ' + param + ' for ' + self.name + ' skipped, because there is no change in the set value.')
            return None
        if param == 'chopper_frequency':
            self.instrument.write(f':wgen:freq {param_val}')
        if param == 'duty_cycle_percent':
            self.instrument.write(f':wgen:func:squ:dcyc {param_val}')
        if param == 'mod_volt_high_in_volt':
            self.instrument.write(f':wgen:volt:high {param_val}')
        if param == 'mod_volt_low_in_volt':
            self.instrument.write(f':wgen:volt:low {param_val}')
   

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)
        if self.total_scan_index == 0:
            self.instrument.write(':wgen:outp 1')

    def data_acquisition_finish(self, **kwargs):
        super().data_acquisition_finish(**kwargs)
        if self.total_scan_index >= 2 * self.scan_num - 1:
            self.instrument.write(':wgen:outp 0')

class RotationStage(Instrument):
    _driver_module = None

    def __init__(self, address=55425494, position_parameters=None, name=None,**kwargs):
        super().__init__(address=address, channel_num=0, 
                         name=name,
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         **kwargs)
        
        if RotationStage._driver_module is None:
            from external_instrument_drivers import K10CR1 as K10CR1
            RotationStage._driver_module = K10CR1
        
       
        self.params = {'angle':0}
        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        self.logger.info('Important: make sure you are not running Kinesis software in the meantime. \nOtherwise the initialization will fail.')
        self.instrument = K10CR1.K10CR1_stage(serial_no=self.address)
        self.instrument.initialize_instrument()
        self.instrument.home_device()

    def quit(self, **kwargs):
        
        # self.instrument.quit()
        super().quit(**kwargs)

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)
        if param_val == self.params_state[param]:
            self.logger.info('Writing ' + param + f' at level {param_val} skipped, because there is no change in the set value.' )
            return None
        self.instrument.move(param_val)
        self.logger.info('Moved ' + self.name + f' to {param_val}.')

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)

class DAQ(Instrument):
    def __init__(self, 
                 address='Dev2', 
                 position_parameters=None, 
                 name=None,
                 input_mapping=['ai0'],
                 no_average_input_channels=[],
                 input_average=1,
                 scan_parameters=None,
                 **kwargs):
        super().__init__(address, channel_num=len(input_mapping), 
                         name=name,
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         channel_name_list=input_mapping,
                         **kwargs)
        
     
        self.input_mapping = input_mapping
        self.scan_parameters = scan_parameters
        self.position_parameters = position_parameters
        self.input_average = int(input_average)
        self.no_average_input_channels = no_average_input_channels
        
        if self.input_average < 1:
            raise RuntimeError('Input average factor should be greater than 1.')
        self.params = {}

        self.DAQ_output_data = self.position_parameters.DAQ_output_data
        self.frequency = 1/(self.scan_parameters.point_time_constant * self.position_parameters.x_pixels)
        self.retrace_frequency = 1/(self.scan_parameters.retrace_point_time_constant * self.position_parameters.x_pixels)
        self.output_mapping=['ao0', 'ao1', 'ao2']
        self.pulse_terminal='PFI0'


    def write_data(self, ao_data, frequency):

        num_samples = ao_data.shape[1]
        DAQ_name = self.address
        # print(f'Pixels:{pixels}')
        # print(f'Shape:{ao_data.shape}')
        # Be careful. The input argument frequency is line scan frequency
        # Total time for executing one line = 1/frequency
        # Total time = nsamples / samplerate = pixels / samplerate
        # -> samplerate = pixels * frequency
        input_mapping_full_path = [
            DAQ_name + '/'+ channel_name for channel_name in self.input_mapping]
        output_mapping_full_path = [
            DAQ_name + '/'+ channel_name for channel_name in self.output_mapping]
        sample_rate = num_samples * frequency

        with ni.Task() as ao_task, ni.Task() as ai_task, ni.Task() as pulse_task:

            for output_channel in output_mapping_full_path:
                ao_task.ao_channels.add_ao_voltage_chan(output_channel,
                                                        min_val=-10, max_val=10)
            ao_task.timing.cfg_samp_clk_timing(sample_rate, sample_mode=AcquisitionType.FINITE, samps_per_chan=num_samples)

            for input_channel in input_mapping_full_path:
                ai_task.ai_channels.add_ai_voltage_chan(input_channel,
                                                        min_val=-10, max_val=10)    
            ai_task.timing.cfg_samp_clk_timing(rate=sample_rate * self.input_average, 
                                               sample_mode=AcquisitionType.FINITE, samps_per_chan=num_samples * self.input_average)
            
            pulse_channel = pulse_task.co_channels.add_co_pulse_chan_freq('Dev2/ctr0', freq=sample_rate, duty_cycle=0.25)
            pulse_channel.co_pulse_term = '/' + DAQ_name + '/' + self.pulse_terminal
            pulse_task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.FINITE, samps_per_chan=num_samples)

            ai_task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source='/Dev2/ao/StartTrigger')
            pulse_task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source='/Dev2/ao/StartTrigger')

            ao_writer = AnalogMultiChannelWriter(ao_task.out_stream)
            ao_writer.write_many_sample(np.ascontiguousarray(ao_data))

            ai_task.start()
            pulse_task.start()
            ao_task.start()

            ai_reader = AnalogMultiChannelReader(ai_task.in_stream)
            ai_data = np.zeros((len(input_mapping_full_path), num_samples * self.input_average))
            ai_reader.read_many_sample(ai_data, num_samples * self.input_average, timeout=600)

            ao_task.wait_until_done()
            ai_task.wait_until_done()
            pulse_task.wait_until_done()

            if self.input_average != 1:
                averaged_ai_data = ai_data.reshape(ai_data.shape[0], -1, self.input_average).mean(axis=2)
                sliced_ai_data = ai_data[:, ::self.input_average]
                compiled_ai_data = np.zeros(sliced_ai_data.shape)
                for channel_index, channel in enumerate(self.input_mapping):
                    if self.is_channel_averaged[channel_index]:
                        compiled_ai_data[channel_index] = averaged_ai_data[channel_index]
                    else:
                        compiled_ai_data[channel_index] = sliced_ai_data[channel_index]
                return compiled_ai_data

            return ai_data

    def read_current_output(self):
        with ni.Task() as read_task:
            for channel_id in [0,1,2]:
                read_task.ai_channels.add_ai_voltage_chan(self.address + f"/_ao{channel_id}_vs_aognd", min_val=-10, max_val=10)
            result = np.array(read_task.read()).reshape(-1)
        return result

    def reset(self,destination=np.array([0,0,0]), ramp_steps=50):

        result = self.read_current_output()
        
        ramp_output_data = np.ascontiguousarray(np.linspace(result, destination,num=ramp_steps).T)
        with ni.Task() as write_task:
            for channel in [0,1,2]:
                write_task.ao_channels.add_ao_voltage_chan(self.address + "/ao" + str(channel), min_val=-10, max_val=10)
            # write_task.timing.cfg_samp_clk_timing(ramp_steps, sample_mode=AcquisitionType.FINITE, samps_per_chan=ramp_steps)
            ao_writer = AnalogMultiChannelWriter(write_task.out_stream, auto_start=True)
            ao_writer.write_many_sample(ramp_output_data)

    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        if not all(channel in self.input_mapping for channel in self.no_average_input_channels):
            error_message = f'Error:\nInput channel list is {self.input_mapping}, the input channel that will not be averaged is {self.no_average_input_channels}. \nSome of the non-averaged input channels are not included in the input channel list.'
            self.logger.info(error_message)
            raise RuntimeError(error_message)
        self.is_channel_averaged = [True for _ in self.input_mapping]
        for channel_index, channel in enumerate(self.input_mapping):
            if channel in self.no_average_input_channels:
                self.is_channel_averaged[channel_index] = False

        device = nidaqSystem.local().devices[self.address]
        self.max_ai_sample_rate = device.ai_max_multi_chan_rate
        num_samples = self.position_parameters.DAQ_output_data.shape[2]
        self.attempted_trace_sample_rate = num_samples * self.frequency * self.input_average
        self.attempted_retrace_sample_rate = num_samples * self.retrace_frequency * self.input_average
        if max(self.attempted_retrace_sample_rate, self.attempted_trace_sample_rate) >= self.max_ai_sample_rate:
            error_message = f"\tError: Attempted trace samplerate {self.attempted_trace_sample_rate} or attempted trace samplerate {self.attempted_retrace_sample_rate} greater than max allowed sample rate {self.max_ai_sample_rate}. " + '''
                            Try: 
                            (1) reduce input_average;
                            (2) reduce x_pixels;
                            (3) increate point time constant for trace and/or retrace scan.

                            '''
            self.logger.info(error_message)
            raise RuntimeError(error_message)
        # for device in devices:
        #     print(f'Device: {device.name}')
            # print(f'Max sample rate: {device.ai_max_multi_chan_rate}')
        self.reset(destination=self.position_parameters.center_output)

    def quit(self, **kwargs):
        destination = np.array([0,0,0]) if self.scan_parameters.return_to_zero else self.position_parameters.center_output
        self.reset(destination=destination)
        super().quit(**kwargs)

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)
        frequency = self.frequency if self.trace_flag else self.retrace_frequency
        DAQ_output_data = self.DAQ_output_data[:,self.total_scan_index,:]
        DAQ_input_data = self.write_data(ao_data=DAQ_output_data, 
                                       frequency=frequency)
        
        if len(DAQ_input_data) == 0:
            return
        
        # self.data = np.mean(
        #     DAQ_input_data[:,:,np.newaxis].reshape(len(self.input_mapping),-1,2), 
        #     axis=2)
        self.data = DAQ_input_data

class DAQ_simulated(Instrument):
    def __init__(self, 
                 address='Dev2', 
                 position_parameters=None, 
                 name=None,
                 input_mapping=['ai0'],
                 scan_parameters=None,
                 **kwargs):
        super().__init__(address, channel_num=len(input_mapping), 
                         name=name,
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         channel_name_list=input_mapping,
                         **kwargs)
     
        self.input_mapping = input_mapping
        self.scan_parameters = scan_parameters
        self.position_parameters = position_parameters
        self.params = {}

        self.DAQ_output_data = self.position_parameters.DAQ_output_data
        self.frequency = 1/(self.scan_parameters.point_time_constant * self.position_parameters.x_pixels)
        self.retrace_frequency = 1/(self.scan_parameters.retrace_point_time_constant * self.position_parameters.x_pixels)
        self.output_mapping=['ao0', 'ao1', 'ao2']
        self.pulse_terminal='PFI0'

    def write_data(self, ao_data, frequency):
        num_samples = ao_data.shape[1]
        DAQ_name = self.address
        input_mapping_full_path = [
            DAQ_name + '/'+ channel_name for channel_name in self.input_mapping]

        # ai_data = np.random.normal(size=(len(input_mapping_full_path), num_samples))
        ai_data = np.linspace(np.zeros(len(input_mapping_full_path)),
                              np.ones(len(input_mapping_full_path)), 
                              num=num_samples).T
        # noise = np.random.normal(size=ai_data.shape)
        time.sleep(1/frequency)
        return ai_data 

    def read_current_output(self):
        return np.random.normal(size=3)

    def reset(self,destination=np.array([0,0,0]), ramp_steps=50):
        pass


    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        self.reset(destination=self.position_parameters.center_output)

    def quit(self, **kwargs):
        destination = np.array([0,0,0]) if self.scan_parameters.return_to_zero else self.position_parameters.center_output
        self.reset(destination=destination)
        super().quit(**kwargs)

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)
        frequency = self.frequency if self.trace_flag else self.retrace_frequency
        DAQ_output_data = self.DAQ_output_data[:,self.total_scan_index,:]
        DAQ_input_data = self.write_data(ao_data=DAQ_output_data, 
                                       frequency=frequency)
        
        if len(DAQ_input_data) == 0:
            return
        

        self.data = DAQ_input_data + np.random.normal(loc=self.scan_index, size=DAQ_input_data.shape) + np.linspace(np.zeros(self.channel_num), 2 * self.scan_index * np.ones(self.channel_num),num=self.reading_num).T
