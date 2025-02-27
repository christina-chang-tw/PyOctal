"""
Import all instruments here to shorten the imports
"""
import sys

__platform__ = ("cygwin", "win32") # Windows OS system


from .agilent816xB import Agilent8163B, Agilent8164B
from .agilentE3640 import AgilentE3640A
from .agilentDSO8000 import AgilentDSO8000

from .ametekDSP72XX import AmetekDSP7230, AmetekDSP7265

from .arroyo6301 import Arroyo6301

from .daylightQCL import DaylightQCL

from .exfoXTA50 import EXFOXTA50

from .fiberlabsAMP import FiberlabsAMP

from .keithley2400 import Keithley2400
from .keithley6487 import Keithley6487

from .keysight86100D import Keysight86100D, KeysightFlexDCA
from .keysightE8257D import KeysightE8257D

from .tektronixScope import TektronixScope

from .thorlabsITC40XX import ThorlabsITC4002QCL
from .thorlabsPM100 import ThorlabsPM100

from .ttiTGF3162 import TTiTGF3162

__all__ = [
        "Agilent8163B",
        "Agilent8164B",
        "AgilentE3640A",
        "AgilentDSO8000",
        "AmetekDSP7230",
        "AmetekDSP7265",
        "Arroyo6301",
        "DaylightQCL",
        "EXFOXTA50",
        "FiberlabsAMP",
        "Keithley2400",
        "Keithley6487",
        "Keysight86100D",
        "KeysightE8257D",
        "TektronixScope",
        "ThorlabsITC4002QCL",
        "ThorlabsPM100",
        "TTiTGF3162",
        "KeysightFlexDCA",
    ]

# Windows OS specific modules
if sys.platform in __platform__:
    from .keysightPAS import KeysightILME
    from .thorlabsAPT import ThorlabsAPT
    __all__.extend(["KeysightILME", "ThorlabsAPT"])
