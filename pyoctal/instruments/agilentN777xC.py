from typing import Union, List, Tuple
import sys
import time

import numpy as np
from scipy.signal import find_peaks
from pyvisa import ResourceManager

from pyoctal.instruments.base import BaseInstrument
from pyoctal.utils.error import PARAM_INVALID_ERR, error_message

class AgilentN777xC(BaseInstrument):
    """
    Agilent N77xx Optical Spectrum Analyzer VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """
    def __init__(self, rm: ResourceManager):
        super().__init__(rm=rm)

    def set_wavelength(self, wavelength: float):
        """ Set the detector wavelength [nm]. """
        self.write(f"source0:wavelength {wavelength}nm")
        
        
    def get_wavelength(self) -> List:
        """ Get the detector function result. """
        return self.query_float(f"source0:wavelength?")