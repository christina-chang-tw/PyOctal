"""
Import all sweeps here to shorten the imports
"""
import sys
from lib.instruments import __platform__
# Windows OS specific modules
if sys.platform in __platform__:
    from .dc import DCSweeps
    from .passive import PASILossSweep

from .ac import ACSweeps
from .iv import IVSweeps
from .passive import InstrILossSweep

__all__ = [
    "ACSweeps",
    "IVSweeps",
    "InstrILossSweep"
]