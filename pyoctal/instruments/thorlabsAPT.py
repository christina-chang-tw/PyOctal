# Make sure that the system is Windows OS
from ctypes import WinDLL, pointer

class ThorlabsAPT:
    """
    Thorlabs APT WinDLL Library.

    Parameters
    ----------
    serial: str
        The serial number of the instrument
    """

    def __init__(self, serial: float=83863567):
        aptdll = WinDLL.LoadLibrary("APT.dll")
        aptdll.EnableEventDlg(True)
        aptdll.APTInit()
        aptdll.InitHWDevice(serial)
        self._aptdll = aptdll
        self.serial = serial

    def MOT_GetPosition(self, pos: float):
        return self._aptdll.MOT_GetPosition(self.serial, pointer(pos))

    def MOT_MoveAbsoluteEx(self, abs_pos: float):
        self._aptdll.MOT_MoveAbsoluteEx(self.serial, abs_pos, True)

    @property
    def aptdll(self):
        return self._aptdll