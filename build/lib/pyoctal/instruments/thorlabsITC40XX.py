from pyvisa import ResourceManager

from pyoctal.instruments.base import BaseInstrument
from pyoctal.utils.error import PARAM_OUT_OF_RANGE_ERR, error_message

class ThorlabsITC4002QCL(BaseInstrument):
    """
    Thorlabs ITC4002QCL Benchtop Laser Diode/TEC Controller for QCLs VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """

    def __init__(self, rm: ResourceManager):
        super().__init__(rm=rm)

    def get_curr(self) -> float:
        """ Get current value [A]. """
        return self.query_float("source:current?")

    def get_curr_max(self) -> float:
        """ Get maximum current value [A]. """
        return self.query_float("source:current? max")

    def set_curr(self, curr: float):
        """ Set current value [A]. """
        if curr > self.get_curr_max():
            raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: \
                             {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write(f"source:current {curr}")
