from pyoctal.base import BaseInstrument
from pyoctal.error import PARAM_OUT_OF_RANGE_ERR, error_message

class ThorlabsITC4002QCL(BaseInstrument):
    """
    Thorlabs ITC4002QCL Benchtop Laser Diode/TEC Controller for QCLs VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    """

    def __init__(self, addr: str):
        super().__init__(rsc_addr=addr)

    def get_curr(self) -> float:
        return self.query_float("source:current?")
    
    def get_curr_max(self) -> float:
        return self.query_float("source:current? max")
    
    def set_curr(self, curr: float):
        if curr > self.get_curr_max():
            raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write(f"source:current {curr}")
        