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