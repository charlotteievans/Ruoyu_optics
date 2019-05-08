import clr  # installs DOTNET DLLs
import contextlib
import sys
import time

sys.path.append("C:\\Program Files\\Thorlabs\\Kinesis") #  adds DLL path to PATH

#  DOTNET (x64) DLLs. These need to be UNBLOCKED to be found (right click -> properties -> unblock
#  This uses Python For DotNet NOT IronPython

clr.AddReference("Thorlabs.MotionControl.Benchtop.StepperMotorCLI")  # TDC001 DLL
clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")
clr.AddReference("System")

# It's going to look like there's errors here but that's because I'm installing the DOTNET libraries as if they are
# python packages
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.Benchtop.StepperMotorCLI import BenchtopStepperMotor
from System import Decimal


@contextlib.contextmanager
def connect_bsc102(serial_number):
    """Context manager for Thorlabs BSC102. Inputs: The controller serial number. Outputs two class instances for the
    X and Y channels. Requires Kinesis installation for 64 bit computers and closely follows the API located locally at
    C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Thorlabs\Kinesis\.Net API Help"""
    device = None
    ch = []
    try:
        DeviceManagerCLI.BuildDeviceList()
        # Tell the device manager to get the list of all devices connected to the computer
        serial_numbers = DeviceManagerCLI.GetDeviceList(BenchtopStepperMotor.DevicePrefix70)
        # if you get an error here, change to DevicePrefix40
        # get available BSC102s and check our serial number is correct
        if str(serial_number) not in serial_numbers:
            raise ValueError("BSC102 stepper motor is not connected.")
        device = BenchtopStepperMotor.CreateBenchtopStepperMotor(str(serial_number))
        device.Connect(str(serial_number))
        for i in range(2):  # each channel must be initializd individually
            ch.append(device.GetChannel(i+1))
            ch[i].WaitForSettingsInitialized(5000)
            if not ch[i].IsSettingsInitialized():
                raise ValueError("BSC102 stepper motor initialization timeout")
            ch[i].StartPolling(250)
            time.sleep(0.5)
            ch[i].EnableDevice()
            motorSettings = ch[i].LoadMotorConfiguration(ch[i].DeviceID)
            currentDeviceSettings = ch[i].MotorDeviceSettings
        yield (StepperMotorController(ch[0]), StepperMotorController(ch[1]))
    finally:
        if ch:
            for i in ch:
                i.StopPolling()
        if device:
            device.Disconnect(True)
        else:
            print('BSC102 stepper motor controller communication error')
            raise ValueError


class StepperMotorController:
    def __init__(self, ch):
        """Stepper Motor Controller for Thorlabs BSC102. Inputs are a single channel from the context manager"""
        self._ch = ch
        self.home()

    def move(self, position):
        """Move to absolute position"""
        if position < 0:
            position = 0
        if position > 8:
            position = 8
        self.wait_until_complete()
        self._ch.MoveTo(Decimal(position), 60000)  # do not use waiteventhandler here - there is an error
            # this is a System.Decimal!
        self.wait_until_complete()

    def home(self):
        """Home device. Because this is an open loop, homing should be completed often"""
        self.wait_until_complete()
        self._ch.Home(self._ch.InitializeWaitHandler())

    def is_homed(self):
        """Returns a boolean of whether or not the channel is homed"""
        return self._ch.Status.IsHomed

    def read_position(self):
        """Return an approximate position of channel location"""
        return self._ch.Position

    def wait_until_complete(self):
        """Bypasses device already moving error"""
        while self._ch.Status.IsInMotion or self._ch.Status.IsJogging or self._ch.State != 0 or self._ch.IsDeviceBusy:
            time.sleep(0.1)
