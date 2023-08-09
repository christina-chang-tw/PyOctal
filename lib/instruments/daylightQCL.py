from lib.base import BaseInstrument
from lib.error import *

from collections import namedtuple

class DaylightQCL(BaseInstrument):
    """
    Daylight QCL Control VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    """

    _rcontrol = namedtuple("rcontrol", ["wn", "curr", "freq", "pw", "mode"])

    def __init__(self, addr: str):
        super().__init__(rsc_addr=addr)
        self._range = self._rcontrol(wn=(9260.0, 9999.0), curr=(0.0, 925.0), freq=(1.0, 100.0), pw=(0.04, 0.5), mode=(1.0, 4.0))

    def set_freq(self, freq: float):
        self.value_check(freq, (self._range.freq[0], self._range.freq[1]))
        self.write(f"pulse:freq {freq}")

    def set_curr(self, curr: float):
        self.value_check(curr, (self._range.curr[0], self._range.curr[1]))
        self.write(f":laser:curr {curr}")

    def set_wn(self, wn: float):
        """ set wavenumber """
        self.value_check(wn, (self._range.wn[0], self._range.wn[1]))
        self.write(f"laser:set {wn}")
            
    def set_wn2(self, wn: float):
        """ set wavenumber """
        self.value_check(wn, (self._range.wn[0], self._range.wn[1]))
        self.write("laser:set\s9500")

    def set_pulse_width(self, pw: float):
        self.value_check(pw, (self._range.pw[0], self._range.pw[1]))
        self.write(f"pulse:width {pw}")

    def set_mode(self, mode: int):
        """
        Set scanmode.

        1 = automatic stepscan
        2 = manual stepscan
        3 = forward sweep
        4 = forward_backward sweep
        """
        self.value_check(mode, (self._range.mode[0], self._range.mode[1]))
        self.write(f"scan:mode {mode}")

    def get_freq(self) -> float:
        answer = self.query("pulse:freq?")
        return float(answer[:-2]) # remove the last cell

    def get_curr(self) -> float:
        """ get the current laser current """
        answer = self.query("laser:current:sense?")
        return float(answer[:-2]) # remove the last cell

    def get_wn(self) -> float:
        """ get the current wavenumber """
        answer = self.query("laser:set?")
        return float(answer[:-2])

    def get_awn(self) -> float:
        """ get the current wavenumber """
        answer = self.query("laser:pos?")
        return float(answer[:-2])

    def get_pulse_width(self) -> float:
        """ get the pulsewidth """
        answer = self.query("pulse:width?")
        return float(answer[:-2])

    def get_mode(self) -> str:
        answer = self.query("scan:mode?")
        return float(answer[:-2])
