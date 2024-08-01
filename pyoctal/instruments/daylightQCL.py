from collections import namedTuple

from pyvisa import ResourceManager

from pyoctal.instruments.base import BaseInstrument

class DaylightQCL(BaseInstrument):
    """
    Daylight QCL Control VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """

    _rcontrol = namedTuple("rcontrol", ["wn", "curr", "freq", "pw", "mode"])

    def __init__(self, addr: str, rm: ResourceManager):
        super().__init__(rsc_addr=addr, rm=rm)
        self._range = self._rcontrol(
            wn=(9260.0, 9999.0),
            curr=(0.0, 925.0),
            freq=(1.0, 100.0),
            pw=(0.04, 0.5),
            mode=(1.0, 4.0)
        )

    def set_freq(self, freq: float):
        """ Set frequency [Hz]. """
        self.value_check(freq, (self._range.freq[0], self._range.freq[1]))
        self.write(f"pulse:freq {freq}")

    def set_curr(self, curr: float):
        """ Set current [A]. """
        self.value_check(curr, (self._range.curr[0], self._range.curr[1]))
        self.write(f":laser:curr {curr}")

    def set_wn(self, wn: float):
        """ Set wavenumber """
        self.value_check(wn, (self._range.wn[0], self._range.wn[1]))
        self.write(f"laser:set {wn}")

    def set_pulse_width(self, pw: float):
        """ Set pulse width """
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
        """ Get frequency [Hz]. """
        answer = self.query("pulse:freq?")
        return float(answer[:-2]) # remove the last cell

    def get_curr(self) -> float:
        """ Get current [A]. """
        answer = self.query("laser:current:sense?")
        return float(answer[:-2]) # remove the last cell

    def get_wn(self) -> float:
        """ Get the current wavenumber. """
        answer = self.query("laser:set?")
        return float(answer[:-2])

    def get_awn(self) -> float:
        """ Get the current wave position? (not sure). """
        answer = self.query("laser:pos?")
        return float(answer[:-2])

    def get_pulse_width(self) -> float:
        """ Get the pulsewidth. """
        answer = self.query("pulse:width?")
        return float(answer[:-2])

    def get_mode(self) -> str:
        """ Get the scan mode. """
        answer = self.query("scan:mode?")
        return float(answer[:-2])
