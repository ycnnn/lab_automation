"""
K10CR1_pythonnet
==================

An example of using the K10CR1 integrated rotation stages with python via pythonnet
"""

import clr 
import os 
import time 
import sys

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
    def __init__(self, serial_no=55425494) -> None:
        # print('Important: make sure you are not running Kinesis software in the meantime. \nOtherwise the initialization will fail.')
        self.address = str(serial_no)

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
        print(self.device_info.Description)
        # Load any configuration settings needed by the controller/stage.
        self.device.LoadMotorConfiguration(self.address, DeviceConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)
        motor_config = self.device.LoadMotorConfiguration(self.address)

    def home_device(self, timeout=60000):
        # Call device methods.
        # print("Homing the rotation stage of SN:  " + self.address)
        self.device.Home(timeout)  # 60 second timeout.
        # print("The system is at home position. This position will be referred as 0 degree.")

    def move(self, angle=0):
        while True:
            if angle < 0:
                angle += 360
            else:
                break
        while True:
            if angle > 360:
                angle -= 360
            else:
                break
        new_pos = Decimal(angle)  # Must be a .NET decimal.
        # print("Moving the rotation stage of SN: " + self.address + f' to {new_pos} degrees')
        self.device.MoveTo(new_pos, 60000)  # 60 second timeout.
        # print("Movement finished.")

    def quit(self):
        self.home_device()
        # Stop polling loop and disconnect device before program finishes. 
        self.device.StopPolling()
        self.device.Disconnect()
        # print("Disconnectd the rotation stage of SN: " + self.address)

    

def main():
    """The main entry point for the application"""
    pass
    # stage = K10CR1_stage()
    # stage.initialize_instrument()
    # stage.home_device()
    # time.sleep(1)
    # stage.move(150)
    # time.sleep(1)
    # stage.quit()

        

if __name__ == "__main__":
    main()
