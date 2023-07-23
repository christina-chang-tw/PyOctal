from lib.base import BaseInstrument
from lib.error import *

from collections import namedtuple

class DaylightQCL(BaseInstrument):

    _rcontrol = namedtuple("rcontrol", ["wn", "curr", "freq", "pw", "mode"])

    def __init__(self, addr):
        super().__init__(rsc_addr=addr)
        self._range = self._rcontrol(wn=(9260.0, 9999.0), curr=(0.0, 925.0), freq=(1.0, 100.0), pw=(0.04, 0.5), mode=(1.0, 4.0))

    def set_freq(self, freq):
        if not self._range.freq[0] < freq < self._range.freq[1]:
            raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write(f"pulse:freq {freq}")

    def set_curr(self, value):
        if not self._range.curr[0] < value < self._range.curr[1]:
            raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write(f":laser:curr {value}")

    def set_wn(self, value):
        """ set wavenumber """
        if not self._range.wn[0] < value < self._range.wn[1]:
            raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write(f"laser:set {value}")
            
    def set_wn2(self, value):
        """ set wavenumber """
        if not self._range.wn[0] < value < self._range.wn[1]:
            raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write("laser:set\s9500")

    def set_pulse_width(self, pw):
        if not self._range.pw[0] < pw < self._range.pw[1]:
            raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write(f"pulse:width {pw}")

    def set_mode(self, mode):
        """set scanmode.

        1 = automatic stepscan
        2 = manual stepscan
        3 = forward sweep
        4 = forward_backward sweep
        """
        if not self._range.mode[0] < mode < self._range.mode[1]:
            raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write(f"scan:mode {mode}")

    def get_freq(self):
        answer = self.query_float("pulse:freq?")
        return answer[:-2] # remove the last cell

    def get_curr(self):
        """ get the current laser current """
        answer = self.query_float("laser:current:sense?")
        return answer[:-2] # remove the last cell

    def get_wn(self):
        """ get the current wavenumber """
        answer = self.query_float("laser:set?")
        return answer[:-2]

    def get_awn(self):
        """ get the current wavenumber """
        answer = self.query_float("laser:pos?")
        return answer[:-2]
    
    def get_pulse_width(self):
        """ get the pulsewidth """
        answer = self.query_float("pulse:width?")
        return answer[:-2]
    
    def get_mode(self):
        answer = self.query_float("scan:mode?")
        return answer[:-2] 
