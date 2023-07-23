from lib.base import BaseInstrument
from lib.error import *

class ThorlabsITC4002QCL(BaseInstrument):
    """
    Thorlabs ITC4002QCL 
    Benchtop Laser Diode/TEC Controller for QCLs VISA Library

    Parameters
    ----------
    addr: str
        The address of the instrument
    """

    def __init__(self, addr):
        super().__init__(rsc_addr=addr)

    def get_curr(self):
        return self.query_float("source:current?")
    
    def get_curr_max(self):
        return self.query_float("source:current? max")
    
    def set_curr(self, curr):
        if curr > self.get_curr_max():
            ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write(f"source:current {curr}")