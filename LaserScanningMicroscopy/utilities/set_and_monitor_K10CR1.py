import os
import clr 
import os 
import time 
import sys
import pyvisa

# Write in file paths of dlls needed. 
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.IntegratedStepperMotorsCLI.dll")

# Import functions from dlls. 
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
from System import Decimal 


class K10CR1_stage:
    def __init__(self, serial_no=55425494, verbose=True, velocity=20.0) -> None:
        print('Important: make sure you are not running Kinesis software in the meantime. \nOtherwise the initialization will fail.')
        self.address = str(serial_no)
        self.verbose = verbose
        self.velocity = velocity

    def initialize_instrument(self):
        DeviceManagerCLI.BuildDeviceList()
        self.device = CageRotator.CreateCageRotator(self.address)
        self.device.Connect(self.address)

        if not self.device.IsSettingsInitialized():
            self.device.WaitForSettingsInitialized(10000)  # 10 second timeout.
            assert self.device.IsSettingsInitialized() is True
        
        # Start polling loop and enable device.
        self.device.StartPolling(250)  #250ms polling rate.
        time.sleep(2)
        self.device.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable.

        # Get Device Information and display description.
        self.device_info = self.device.GetDeviceInfo()
        if self.verbose:
            print(self.device_info.Description)
        # Load any configuration settings needed by the controller/stage.
        self.device.LoadMotorConfiguration(self.address, DeviceConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)
        motor_config = self.device.LoadMotorConfiguration(self.address)

        # self.device.SetVelocityParams(self.device.GetVelocityParams())
        self.VelocityParams = self.device.GetVelocityParams()
        self.VelocityParams.MaxVelocity = Decimal(self.velocity)
        self.device.SetVelocityParams(self.VelocityParams)


    def home_device(self, timeout=60000):
        # Call device methods.
        if self.verbose:
            print("Homing the rotation stage of SN:  " + self.address)
        self.device.Home(timeout)  # 60 second timeout.
        if self.verbose:
            print("The system is at home position. This position will be referred as 0 degree.")

    def move(self, angle=0):

        while True:
            if angle < 0:
                angle = angle + 360.0
            else:
                break
        while True:
            if angle > 360.0:
                angle = angle - 360.0
            else:
                break
        new_pos = Decimal(angle)  # Must be a .NET decimal.
        if self.verbose:
            print("Moving the rotation stage of SN: " + self.address + f' to {new_pos} degrees')
        self.device.MoveTo(new_pos, 60000)  # 60 second timeout.
        if self.verbose:
            print("Movement finished.")

    def read(self):
        return Decimal.ToDouble(self.device.Position)

    def quit(self):
        self.home_device()
        # Stop polling loop and disconnect device before program finishes. 
        self.device.StopPolling()
        self.device.Disconnect()
        if self.verbose:
            print("Disconnectd the rotation stage of SN: " + self.address)
    
# class PowerMeter:
#     def __init__(self, address='USB0::0x1313::0x8078::P0011410::INSTR'):
#         self.rm = pyvisa.ResourceManager()
#         self.pm = self.rm.open_resource('USB0::0x1313::0x8078::P0011410::INSTR')
#         self.pm.write("SENS:RANGE:AUTO ON")
#         self.pm.write("SENS:CORR:WAV 658")
#         #set units to Watts
#         self.pm.write("SENS:POW:UNIT W")
#         #set averaging to 1000 points
#         self.pm.write("SENS:AVER:1000")

#     def measure(self):
#         power = self.pm.query_ascii_values("MEAS:POW?")[0]
#         return power
    
#     def close(self):
#         self.pm.close()
#         self.rm.close()


if __name__ == '__main__':


    stage = K10CR1_stage(serial_no=55425494)
    stage.initialize_instrument()

    stage.home_device()
    stage.move(30)

    stage.quit()
