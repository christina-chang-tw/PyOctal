"""
Import all sweeps here to shorten the imports
"""
import sys
from pyoctal.instruments import __platform__
# Windows OS specific modules
if sys.platform in __platform__:
    from .dc import DCSweeps
    from .passive import ILossSweep
    from .amp import AMPSweeps

from .ac import ACSweeps
from .iv import IVSweeps

__all__ = [
    "ACSweeps",
    "IVSweeps",
    "InstrILossSweep"
]