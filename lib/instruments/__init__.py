"""
Import all instruments here to shorten the imports
"""

from lib.util.util import platform_check
platform_check()

from .agilent8163B import Agilent8163B
from .agilentE364X import AgilentE3645, AgilentE3640A
from .agilentDSO8000 import AgilentDSO8000

from .ametekDSP72XX import AmetekDSP7230, AmetekDSP7265

from .arroyo6301 import Arroyo6301

from .daylightQCL import DaylightQCL
from .dummy import DummyILME, DummyMultimeter, DummyPowerSupply

from .keithley2400 import Keithley2400
from .keithley6487 import Keithley6487

from .keysight86100D import Keysight86100D
from .keysightE8257D import KeysightE8257D

from .keysightPAS import AgilentILME

from .tektronixScope import TektronixScope

from .thorlabsITC40XX import ThorlabsITC4002QCL
from .thorlabsPM100 import ThorlabsPM100
from .thorlabsAPT import ThorlabsAPT

from .ttiTGF3162 import TTiTGF3162

__all__ = [
    "Agilent8163B",
    "AgilentE3645",
    "AgilentE3640A",
    "AgilentDSO8000",
    "AmetekDSP7230",
    "AmetekDSP7265",
    "Arroyo6301",
    "DaylightQCL",
    "Keithley2400",
    "Keithley6487",
    "Keysight86100D",
    "KeysightE8257D",
    "AgilentILME",
    "TektronixScope",
    "ThorlabsITC4002QCL",
    "ThorlabsPM100",
    "ThorlabsAPT",
    "TTiTGF3162",
]
