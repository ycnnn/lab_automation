import os
import time
from lakeshore import Model335, Model335InputSensorSettings

class temprature_controller:

    def __init__(self):
        #Initialization

        # Connect to the first available Model 335 temperature controller over USB using a baud rate of 57600
        self.instrument = Model335(57600)

        # Create a new instance of the input sensor settings class
        self.sensor_settings = Model335InputSensorSettings(self.instrument.InputSensorType.DIODE, True, False,
                                                    self.instrument.InputSensorUnits.KELVIN,
                                                    self.instrument.DiodeRange.TWO_POINT_FIVE_VOLTS)

        # Apply these settings to input A of the instrument
        self.instrument.set_input_sensor("A", self.sensor_settings)

        # Set diode excitation current on channel A to 10uA
        self.instrument.set_diode_excitation_current("A", self.instrument.DiodeCurrent.TEN_MICROAMPS)

    def measure(self):
        self.data = self.instrument.get_all_kelvin_reading()[0]
        return self.data
    
    def heat(self, temp_set_point=4.00):
        self.temp_set_point = temp_set_point
        self.instrument.set_control_setpoint(1,self.temp_set_point)
        self.measure()
        temp_difference = self.data - self.temp_set_point
        if temp_difference >= -1E-1:
            self.instrument.set_heater_range(1, self.instrument.HeaterRange.OFF)
        elif abs(temp_difference) <= 20.0:
            self.instrument.set_heater_range(1, self.instrument.HeaterRange.LOW)
        elif abs(temp_difference) <= 50.0:
            self.instrument.set_heater_range(1, self.instrument.HeaterRange.MEDIUM)
        elif abs(temp_difference) <= 300.0:
            self.instrument.set_heater_range(1, self.instrument.HeaterRange.HIGH)
        else:
            self.instrument.set_heater_range(1, self.instrument.HeaterRange.OFF)
            raise RuntimeError
        

if __name__=='__main__':

    instr = temprature_controller()
    curr_temp = instr.measure()
    # Measure the temperatre every 5 seconds
    interval = 5
    temp_list = []

    for ind in range(1000000):
        time.sleep(interval)
        new_temp = instr.measure()
        temp_list.append(new_temp)
        print(f'Time = {interval * ind} s')
        print(f'New temprature = {new_temp:.2f} K, the temp changed {(new_temp - curr_temp):.2f} K in {interval} seconds  >>>>', end='\n\n')
        curr_temp= new_temp
