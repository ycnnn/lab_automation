import sys, time
from contextlib import contextmanager
import numbers
import pyvisa
import numpy as np

import nidaqmx as ni
from nidaqmx.constants import WAIT_INFINITELY
from nidaqmx.constants import Edge, AcquisitionType, TaskMode, WAIT_INFINITELY
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogMultiChannelWriter


class Instrument:
    def __init__(self, 
                 address, 
                 channel_num, 
                 steps,
                 channel_name_list=None,
                 **kwargs):
        self.name = self.__class__.__name__
        self.address = address

        # self.logger = Logger(os.path.dirname(os.path.realpath(__file__)) + '/')
        self.channel_num = channel_num
        self.hysteresis = False

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


        self.steps = steps
        self.data = np.zeros(shape=(self.channel_num))
        # self.params stores the default parameter setting for the instrument
        self.params = {}
        # self.customized_params are the customized parameter setting 
        # for the instrument from the user
        self.customized_params = kwargs
        # self.params_sweep_lists stores the instrument parameter for each trace 
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

    def sweep_parameter_generator(self, param, param_val):

        if isinstance(param_val, numbers.Number):
            # Single input value, the parameter is fixed throughout the scan
            param_sweep_list = param_val * np.ones(shape=(self.steps))
        elif isinstance(param_val, list) and len(param_val) == 2:
            # Double input value, 
            # If input is of format [start, end], the parameter is sweeped from left_val to right_val
            start_val, end_val = param_val
            param_sweep_list = np.linspace(start_val,end_val,num=self.steps)
        else:
            # Customizable paraeter sweep list. Must be a np.ndarray
            # Must have shape of (self.steps,); that is, it is a single 1D array
            if (not isinstance(param_val, np.ndarray)) or param_val.shape!= (self.steps):
                error_message = '\n\nError when setting up ' + param + ' for ' +  self.name + ': the user either enetered the wrong parameter format, or indicated customized paramter sweep list, but does not supply a list of correct shape. Acceptable formats: a number, or a tuple of (start_val, end_val), or a numpy array of shape (2, steps).'
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

    @contextmanager
    def initialize_and_quit(self, **kwargs):
        # First assign the logger
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

    def initialize(self, **kwargs):
        self.set_up_parameter_list()
        self.logger.info('Initialized ' + self.name)
   
    def quit(self, **kwargs):
        self.logger.info('Quitted ' + self.name)

    def write_param_to_instrument(self, param, target_val):
        return None

    def data_acquisition_start(self, **kwargs):

        self.scan_index = int(kwargs['scan_index'])
       
        self.logger.info(self.name + f' Scanning at scan_index {self.scan_index}')
        ramp_data = {}

        for param, param_sweep_list in self.params_sweep_lists.items():
            target_val = param_sweep_list[self.scan_index]
            ramp_data[param] = self.write_param_to_instrument(param, target_val)
            self.logger.info('At ' + f' scan {self.scan_index}, ' + param + ' for ' + self.name + f' set to {target_val}.')
            self.params_state[param] = target_val
        return ramp_data
    
    def data_acquisition_finish(self, **kwargs):
        return None
    
class EmptyInstrument(Instrument):
    def __init__(self, address, scan_parameters, **kwargs):
        super().__init__(address, channel_num=0, 
                         steps=scan_parameters.steps, 
                         **kwargs)

    def initialize(self, **kwargs):
        super().initialize(**kwargs)
  
    def quit(self, **kwargs):
        super().quit(**kwargs)

    def data_acquisition_start(self, **kwargs):
        pass


class SimulatedInstrument(Instrument):
    def __init__(self, address, scan_parameters, wait=0.1, name=None,**kwargs):
        super().__init__(address, channel_num=1, 
                         steps=scan_parameters.steps, 
                         channel_name_list=['Sim_instr'],
                         **kwargs)
        # self.steps = scan_parameters.steps
        self.name = self.name if not name else name
        self.params = {'param1':20, 'param2':[0,1], 'param3':0}
        self.wait = wait
        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)

    def quit(self, **kwargs):
        super().quit(**kwargs)

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)

    def data_acquisition_start(self, **kwargs):
        time.sleep(self.wait)
        ramp_data = super().data_acquisition_start(**kwargs)

        self.data = np.cos(np.ones(
                shape=(self.channel_num)) * self.scan_index)
        # self.data = np.cos(self.params_sweep_lists['param2'][self.scan_index])
  
class SMU(Instrument):
    def __init__(self, scan_parameters, 
                 address="USB0::0x05E6::0x2450::04096331::INSTR",
                 name=None,
                 ramp_steps=5,
                 mode='Force_V_Sense_V',
                 **kwargs):
        
        super().__init__(address, channel_num=1, 
                         steps=scan_parameters.steps, 
                         channel_name_list=['Measure'],
                         **kwargs)
        
        self.name = self.name if not name else name
        self.ramp_steps = ramp_steps
        self.mode = mode
        self.params = {'Source':0}

        if self.mode =='Force_V_Sense_V' or self.mode =='Force_V_Sense_I':
            pass
        else:
            raise RuntimeError('\n\n mode: ' + self.mode + ' not supoorted. Either Force_V_Sense_V or Force_V_Sense_I.\n\n')
    

        
    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        rm = pyvisa.ResourceManager()
        self.smu = rm.open_resource(self.address)

        self.smu.write("smu.source.func = smu.FUNC_DC_VOLTAGE")
        self.smu.write("smu.measure.func = smu.FUNC_DC_VOLTAGE")
        self.smu.write('smu.source.output = smu.ON')

        source_target = self.params_sweep_lists['Source'][0]
        source_ramp = np.linspace(0, source_target, num=self.ramp_steps)

        for source_val in source_ramp:
            self.smu.write(f'smu.source.level = {source_val}')
            self.smu.write('smu.measure.read()')

        if self.mode =='Force_V_Sense_V':
            pass
        elif self.mode =='Force_V_Sense_I':
            self.smu.write("smu.measure.func = smu.FUNC_DC_CURRENT")
        else:
            pass
      
  
    def quit(self, **kwargs):

        if self.mode =='Force_V_Sense_V':
            pass
        elif self.mode =='Force_V_Sense_I':
            self.smu.write("smu.measure.func = smu.FUNC_DC_VOLTAGE")
        else:
            pass

        # self.smu.write("smu.measure.func = smu.FUNC_DC_VOLTAGE")
        self.smu.write('reading = smu.measure.read()')
        measured_data = self.smu.query_ascii_values('print(reading)')[0]
       
        source_quit = np.linspace(measured_data, 0, num=self.ramp_steps)
       
        for source_val in source_quit:
            self.smu.write(f'smu.source.level = {source_val}')
            self.smu.write('smu.measure.read()')

        self.smu.write('smu.source.output = smu.OFF')

        super().quit(**kwargs)

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(None, None)
        self.smu.write(f'smu.source.level = {param_val}')
       
        return param_val

    def data_acquisition_start(self, **kwargs):
        
        super().data_acquisition_start(**kwargs)
        self.smu.write('reading = smu.measure.read()')
        measured_data = self.smu.query_ascii_values('print(reading)')[0]
        self.data = np.ones(shape=(self.channel_num)) * measured_data
   

class Lockin(Instrument):
    def __init__(self, 
                 address="USB0::0xB506::0x2000::002765::INSTR", 
                 scan_parameters=None, 
                 name=None, 
                 initial_wait_cycles=20,
                 **kwargs):
        super().__init__(address, channel_num=4, 
                         steps=scan_parameters.steps, 
                         channel_name_list = ['X', 'Y', 'X_noise', 'Y_noise'],
                         **kwargs)
        
        self.name = self.name if not name else name

        self.params = {'time_constant_level':8, 
                        'volt_input_range':3, 
                        'signal_sensitivity':12,
                    }
        self.initial_wait_cycles = initial_wait_cycles
        
        
    def time_constant_conversion(self, input_value, code_to_analog=False):
        # Conversion table (time code -> time duration)
        time_table = {
            0: 1e-6,    # 1us
            1: 3e-6,    # 3us
            2: 10e-6,   # 10us
            3: 30e-6,   # 30us
            4: 100e-6,  # 100us
            5: 300e-6,  # 300us
            6: 1e-3,    # 1ms
            7: 3e-3,    # 3ms
            8: 10e-3,   # 10ms
            9: 30e-3,   # 30ms
            10: 100e-3, # 100ms
            11: 300e-3, # 300ms
            12: 1,      # 1s
            13: 3,      # 3s
            14: 10,     # 10s
            15: 30,     # 30s
            16: 100,    # 100s
            17: 300,    # 300s
            18: 1000,   # 1000s
            19: 3000,   # 3000s
            20: 10000,  # 10000s
        }

        # Convert from time code to time (seconds)
        if code_to_analog:
            if 0 <= input_value <= 20:
                return time_table[input_value]
            else:
                raise ValueError("Invalid time code. Must be an integer between 0 and 20.")

        # Convert from time to time code
        else:
            if input_value > 0:
                # Find the closest time code that fits
                for code in range(20, -1, -1):  # Start from the largest value
                    if input_value >= time_table[code] * 0.9998:
                        return code
                return 0  # If input_value is less than the smallest time code (1us)
            else:
                raise ValueError("Invalid time value. Must be a positive number.")

    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(self.address)
        # Reset
        self.instrument.write('*rst')
        # self.logger.info(self.instrument.query('*idn?'))


        # # build buffer
        # self.instrument.write('capturelen 256')
        # # record XY signals
        # self.instrument.write('capturecfg xy')


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
        self.instrument.write(f"irng {self.params_sweep_lists['volt_input_range'][0]}")
        # self.logger.info(self.instrument.query('irng?'))

        # Set the signal sensitivity
        # Levels and range: 0->1V, 1->500mV, 2->200mV 3->100mV, 4->50mV, 5->20mV, 6->10mV, 7->5mV, 8->2mV, 
        # 9->1mV, 10->500uV, 11->200uV, 12->100uV, 13->50uV, 14->20uV
        self.instrument.write(f"scal {self.params_sweep_lists['signal_sensitivity'][0]}")
        # self.logger.info(self.instrument.query('scal?'))

        # Set the time constant
        # Levels and range: 0->1us, 1->3us, 2->10us 3->30us, 4->100us, 5->300us, 6->1ms, 7->3ms, 8->10ms, 
        # 9->30ms, 10->100ms, 11->300ms, 12->1s, 13->3s, 14->10s, 15->30s, 16->100s, 17->300s, 18->1000s, 19->3000s, 20->10000s
        self.instrument.write(f"oflt {self.params_sweep_lists['time_constant_level'][0]}")
        # self.logger.info(self.instrument.query('oflt?'))

        # Set the reference mode as external reference
        self.instrument.write(f"rsrc 1")
        # Set the external reference trigger mode as positive TTL
        self.instrument.write(f"rtrg 1")
        # Set the external reference trigger input to 1 MOhm
        self.instrument.write(f"refz 1")

        wait_time = self.initial_wait_cycles * self.time_constant_conversion(self.params_sweep_lists['time_constant_level'][0],
                                                         code_to_analog=True)
    
        self.logger.info(f'Lockin wait initial {wait_time} s for signal acquisition')
        time.sleep(wait_time)


        # Set the amplitude of the sine output signal 
        # self.instrument.write(f"slvl {self.params_sweep_lists['sine_amplitude'][0,0]}")
        # self.logger.info(self.instrument.query('slvl?'))

    def quit(self, **kwargs):
        super().quit(**kwargs)
        # Disconnect 
        self.instrument.close()

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)

        if self.params_state[param] == param_val:
            self.logger.info('Writing ' + param + f' at level {param_val} skipped, because there is no change in the set value.' )
            return None

        if param == 'time_constant_level':
            self.instrument.write(f"oflt {int(param_val)}")
        elif param == 'volt_input_range':
            self.instrument.write(f"irng {int(param_val)}")
        elif param == 'signal_sensitivity':
            self.instrument.write(f"scal {int(param_val)}")
        
        return None

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)
        # Wait one cycle of time constant
        wait_time = 1.10 * self.time_constant_conversion(self.params_sweep_lists['time_constant_level'][self.scan_index],
                                                         code_to_analog=True)
        self.logger.info(f'Lockin wait {wait_time} s for signal acquisition')
        time.sleep(wait_time)

    def data_acquisition_finish(self, **kwargs):
        super().data_acquisition_finish(**kwargs)

        # time.sleep(1)
        x_data, y_data = self.instrument.query_ascii_values('snap? 1,2')
        x_noise, y_noise = self.instrument.query_ascii_values('snap? 8,9')

        self.data = np.array([x_data, y_data, x_noise, y_noise])      
  

class LaserDiode(Instrument):
    def __init__(self, address='USB0::0x1313::0x804F::M00423181::INSTR', 
                 scan_parameters=None, 
                 always_on_during_scan=True,
                 name=None, 
                 **kwargs):
        
        super().__init__(address, channel_num=0, 
                         steps=scan_parameters.steps, 
                         **kwargs)
        
        self.name = self.name if not name else name
        self.params = {'current':0.01}
        self.always_on_during_scan = always_on_during_scan
        
        
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

        self.instrument.write(f"source1:current:level:amplitude {self.params_sweep_lists['current'][0]}")
        self.instrument.write('output:state 1')

    def quit(self, **kwargs):
        super().quit(**kwargs)
        self.instrument.write('output:state 0')
        self.instrument.close()

    def write_param_to_instrument(self, param, param_val):
        super().write_param_to_instrument(param, param_val)
        if param_val == self.params_state[param]:
            self.logger.info('Writing ' + param + ' for ' + self.name + ' skipped, because there is no change in the set value.')
        self.instrument.write(f"source1:current:level:amplitude {param_val}")

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)
        # if self.scan_index == 0:
        #     self.instrument.write('output:state 1')

    def data_acquisition_finish(self, **kwargs):
        super().data_acquisition_finish(**kwargs)
        if self.scan_index >= self.steps - 1:
            self.instrument.write('output:state 0')


class DAQ(Instrument):
    def __init__(self, 
                 address='Dev2', 
                 scan_parameters=None, 
                 name=None,
                 input_mapping=['ai0'],
                 **kwargs):
        super().__init__(address, channel_num=len(input_mapping), 
                         steps=scan_parameters.steps, 
                         channel_name_list=input_mapping,
                         **kwargs)
        
        self.name = self.name if not name else name
        self.input_mapping = input_mapping
        self.scan_parameters = scan_parameters
        self.position_parameters = scan_parameters.position_parameters
        self.params = {}

        self.DAQ_output_data = self.position_parameters.DAQ_output_data
    
        self.output_mapping=['ao0', 'ao1', 'ao2']


    def write_data(self, ao_data):

        DAQ_name = self.address

        input_mapping_full_path = [
            DAQ_name + '/'+ channel_name for channel_name in self.input_mapping]
        output_mapping_full_path = [
            DAQ_name + '/'+ channel_name for channel_name in self.output_mapping]
        
        with ni.Task() as ao_task, ni.Task() as ai_task:
            for ao_channel in output_mapping_full_path:
                ao_task.ao_channels.add_ao_voltage_chan(ao_channel)
            for ai_channel in input_mapping_full_path:
                ai_task.ai_channels.add_ai_voltage_chan(ai_channel)
            ao_task.write(np.ascontiguousarray(ao_data))
            ai_data = ai_task.read(number_of_samples_per_channel=1)

        # print('\n\n\n\nDAQ data:\n\n\n\n')
        # print(ai_data)
        # print('\n\n\n\n\n\n\n\n')
        return np.array(ai_data).reshape(-1)

      

    def read_current_output(self):
        with ni.Task() as read_task:
            for channel_id in [0,1,2]:
                read_task.ai_channels.add_ai_voltage_chan(self.address + f"/_ao{channel_id}_vs_aognd", min_val=-10, max_val=10)
            result = np.array(read_task.read()).reshape(-1)
        return result

    def reset(self,destination=np.array([0,0,0]), ramp_steps=20):

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
        self.reset(destination=self.position_parameters.center_output)

    def quit(self, **kwargs):
        super().quit(**kwargs)
        destination = np.array([0,0,0]) if self.scan_parameters.position_parameters.return_to_zero else self.position_parameters.center_output
        self.reset(destination=destination)

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)
        DAQ_output_data = self.DAQ_output_data[:,self.scan_index]
        DAQ_input_data = self.write_data(ao_data=DAQ_output_data)
        
        if len(DAQ_input_data) == 0:
            return
        
        self.data = DAQ_input_data

class DAQ_simulated(Instrument):
    def __init__(self, 
                 address='Dev2_sim', 
                 scan_parameters=None, 
                 name=None,
                 input_mapping=['ai0'],
                 **kwargs):
        
        super().__init__(address, channel_num=len(input_mapping), 
                         steps=scan_parameters.steps, 
                         channel_name_list=input_mapping,
                         **kwargs)
        
        self.name = self.name if not name else name
        self.input_mapping = input_mapping
        self.scan_parameters = scan_parameters
        self.position_parameters = scan_parameters.position_parameters
        self.params = {}

        self.DAQ_output_data = self.position_parameters.DAQ_output_data

        self.output_mapping=['ao0', 'ao1', 'ao2']


    def write_data(self, ao_data):
        DAQ_name = self.address
        input_mapping_full_path = [
            DAQ_name + '/'+ channel_name for channel_name in self.input_mapping]

        ai_data = np.random.normal(size=(len(input_mapping_full_path)))
        return ai_data

    def read_current_output(self):
        return np.random.normal(size=3)

    def reset(self,destination=np.array([0,0,0]), ramp_steps=50):
        pass

    def initialize(self, **kwargs):
        super().initialize(**kwargs)
        self.reset(destination=self.position_parameters.center_output)

    def quit(self, **kwargs):
        super().quit(**kwargs)
        destination = np.array([0,0,0]) if self.scan_parameters.position_parameters.return_to_zero else self.position_parameters.center_output
        self.reset(destination=destination)

    def data_acquisition_start(self, **kwargs):
        super().data_acquisition_start(**kwargs)
        
        DAQ_output_data = self.DAQ_output_data[:,self.scan_index]
        DAQ_input_data = self.write_data(ao_data=DAQ_output_data)
        
        if len(DAQ_input_data) == 0:
            return

        self.data = DAQ_input_data
