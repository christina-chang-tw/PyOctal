from lib.base import BaseInstrument
from lib.error import *

from collections import namedtuple

class ThorlabsQCL(BaseInstrument):

    _control = namedtuple("control", ["wn", "freq", "pw", "startwn", "stopwn", "rate", "cycles", "mode", "pause", "step", "interval"])
    _state = namedtuple("state", ["wn", "freq", "pw", "startwn", "stopwn", "rate", "cycles", "mode", "pause", "step", "whours", "scancount", "interval", "awn"])
    _query = namedtuple("query", ["wn", "freq", "pw", "startwn", "stopwn", "rate", "cycles", "mode", "pause", "step", "whours", "scancount", "awn", "all"])

    def __init__(self, addr):
        super().__init__(rsc_addr=addr)
        self.wn_range=tuple(9260, 9999)

    def set_curr(self, value):
        if not 0 < value < 925:
            raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write(f":laser:curr {value}")

    def set_wn(self, value):
        """ set wavenumber """
        if not self.wn_range[0] < value < self.wn_range[1]:
            raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write(f"laser:set {value}")

            
    def set_wn2(self, value):
        """ set wavenumber """
        if not self.wn_range[0] < value < self.wn_range[1]:
            raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write("laser:set\s9500")


    def get_curr(self):
        """ get the current laser current """
        answer = self.query_float("laser:current:sense?")
        return answer[:-2] # remove the last cell

    def get_wn(self):
        """ get the current wavenumber """
        answer = self.query_float(":laser:set?")
        return answer[:-2]

    def get_awn(self):
        """ get the current wavenumber """
        answer = self.query_float(":laser:pos?")
        return answer[:-2]
