"""Simultaneous read and write with NI USB-4431 or similar device."""

import numpy as np
import numbers
import os
import pyvisa
from contextlib import contextmanager
import warnings
# from pathlib import Path
from external_instrument_drivers import K10CR1 as K10CR1
import time
# from source.logger import Logger
from source.daq_driver import daq_interface, reset_daq


class Instrument:

    # log_file_path = os.path.dirname(os.path.dirname(__file__)) + '/temp_files/temp_instr_log.txt'
    # logger = Logger(log_file_path)

    def __init__(self, 
                 address, 
                 channel_num, 
                 reading_num, 
                 scan_num,
                 channel_name_list=None,
                 **kwargs):
        
        self.name = self.__class__.__name__
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
                error_message = '\n\nError when setting up ' + param + ' for ' +  self.name + ': the user either enetered the wrong parameter format, or indicated customized paramter sweep list, but does not supply a list of correct shape. Acceptable formats: a number, or a tuple of (start_val, end_val), or a numpy array of shape (2, scan_num).'
                self.logger.info(error_message)
                raise TypeError(error_message)
            param_sweep_list = param_val
        
        return param_sweep_list
    
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
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         channel_name_list=['Sim_instr'],
                         **kwargs)
        
        self.name = self.name if not name else name

        self.params = {'param1':20, 'param2':[0,1], 'param3':0}
        
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
  
class SMU(Instrument):
    def __init__(self, position_parameters, 
                 address="USB0::0x05E6::0x2450::04096331::INSTR",
                 name=None,
                 ramp_steps=10,
                 **kwargs):
        
        super().__init__(address, channel_num=1, 
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         channel_name_list=['Voltage'],
                         **kwargs)
        
        self.name = self.name if not name else name
        self.ramp_steps = ramp_steps
        self.params = {'voltage':0}

        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        rm = pyvisa.ResourceManager()
        self.logger.info('\n\nIntializing...\n\n')
        self.smu = rm.open_resource(self.address)
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
        super().quit(**kwargs)
        self.write_param_to_instrument('voltage', 0)
        self.smu.write('smu.source.output = smu.OFF')

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
        

class Lockin(Instrument):
    def __init__(self, 
                 address="USB0::0xB506::0x2000::002765::INSTR", 
                 position_parameters=None, 
                 name=None, 
                 **kwargs):
        super().__init__(address, channel_num=2, 
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         channel_name_list = ['X', 'Y'],
                         **kwargs)
        
        self.name = self.name if not name else name

        self.params = {'time_constant_level':9, 
                        'volt_input_range':2, 
                        'signal_sensitivity':6,
                        'ref_frequency':20170,
                        'sine_amplitude':1,
                                  }
        
        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)

        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(self.address)

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

        # Set the reference frequency of the sine output signal as 20.17 kHz
        self.instrument.write(f"freq {self.params_sweep_lists['ref_frequency'][0,0]}")
        # self.logger.info(self.instrument.query('freq?'))

        # Set the amplitude of the sine output signal 
        self.instrument.write(f"slvl {self.params_sweep_lists['sine_amplitude'][0,0]}")
        # self.logger.info(self.instrument.query('slvl?'))

    def quit(self, **kwargs):
        super().quit(**kwargs)
        # Turn off sine output
        self.instrument.write(f"slvl 0")
        self.instrument.query('slvl?')
        # Disconnect 
        self.instrument.close()

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
        elif param == 'ref_frequency':
            self.instrument.write(f"freq {param_val}")
        elif param == 'sine_amplitude':
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
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         **kwargs)
        
        self.name = self.name if not name else name

        self.params = {'current':0.01}
        
        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(self.address)
   
        if np.min(
            self.params_sweep_lists['current']
            ) < 0 or np.max(
            self.params_sweep_lists['current']
            ) >= 0.101:
            self.logger.info('Warning: the laser current setpoint is outside the allowed range.\nFor your safety, the laser power has been set to 10 mA.')
            self.current_levels = 0.01 * np.ones(self.params_sweep_lists['current'].shape)

        self.instrument.write(f"source1:current:level:amplitude {self.params_sweep_lists['current'][0,0]}")
        self.instrument.write('output:state 1')

    def quit(self, **kwargs):
        super().quit(**kwargs)
        self.instrument.write('output:state 0')
        self.instrument.write(f"source1:current:level:amplitude 0.01")
        self.instrument.close()

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)
        if param_val == self.params_state[param]:
            self.logger.info('Writing ' + param + ' for ' + self.name + ' skipped, because there is no change in the set value.')
        self.instrument.write(f"source1:current:level:amplitude {param_val}")

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)

class RotationStage(Instrument):
    def __init__(self, address=55425494, position_parameters=None, name=None,**kwargs):
        super().__init__(address=address, channel_num=0, 
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         **kwargs)
        
        self.name = self.name if not name else name
        self.params = {'angle':0}
        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        self.logger.info('Important: make sure you are not running Kinesis software in the meantime. \nOtherwise the initialization will fail.')
        self.instrument = K10CR1.K10CR1_stage(serial_no=self.address)
        self.instrument.initialize_instrument()
        self.instrument.home_device()

    def quit(self, **kwargs):
        super().quit(**kwargs)
        self.instrument.quit()

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)
        if param_val == self.params_state[param]:
            self.logger.info('Writing ' + param + f' at level {param_val} skipped, because there is no change in the set value.' )
            return
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
                 scan_parameters=None,
                 **kwargs):
        super().__init__(address, channel_num=len(input_mapping), 
                         reading_num=position_parameters.x_pixels, 
                         scan_num=position_parameters.y_pixels, 
                         channel_name_list=input_mapping,
                         **kwargs)
        
        self.name = self.name if not name else name
        self.input_mapping = input_mapping
        self.scan_parameters = scan_parameters
        self.position_parameters = position_parameters
        self.params = {}

        self.DAQ_output_data = self.position_parameters.DAQ_output_data
        self.frequency = 1/(self.scan_parameters.point_time_constant * self.position_parameters.x_pixels)
        self.retrace_frequency = 1/(self.scan_parameters.retrace_point_time_constant * self.position_parameters.x_pixels)

    def move_to_origin(self):
     
        DAQ_output_data = self.position_parameters.final_move
        _ = daq_interface(ao0_1_write_data=DAQ_output_data, 
                    frequency=max(1, self.frequency),
                    input_mapping=["ai0"],
                    DAQ_name=self.address)
    
    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        reset_daq(self.scan_parameters, destination=self.position_parameters.center_output)

    def quit(self, **kwargs):
        super().quit(**kwargs)
        self.move_to_origin()
        if self.scan_parameters.return_to_zero:
            reset_daq(self.scan_parameters, destination=np.array([0,0,0,0]))

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)
        frequency = self.frequency if self.trace_flag else self.retrace_frequency
        DAQ_output_data = self.DAQ_output_data[:,self.total_scan_index,:].T
        DAQ_input_data = daq_interface(ao0_1_write_data=DAQ_output_data, 
                                       frequency=frequency,
                                       input_mapping=self.input_mapping,
                                       DAQ_name=self.address)
        
        if len(DAQ_input_data) == 0:
            return
        
        self.data = np.mean(
            DAQ_input_data[:,:,np.newaxis].reshape(len(self.input_mapping),-1,2), 
            axis=2)

