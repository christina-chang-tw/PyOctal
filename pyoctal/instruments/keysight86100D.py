from pyoctal.base import BaseInstrument
from pyoctal.error import *

from typing import Union

class Keysight86100D(BaseInstrument):
    """
    Keysight 86100D Wide-Bandwidth Oscilloscope VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm: str
        Argument for resource manager (for simualated device only)
    chan: int, default = 1
        The input channel
    clk_num: int, default = 1
        The clock recovery number
    """

    def __init__(self, addr: str, rm: str="", chan: int=1, clk_num: int=1):
        super().__init__(rsc_addr=addr, rm=rm)
        self.chan = chan
        self.clk_num = clk_num
        self.channel = f"channel{chan}"
        self.clock = f"crecovery{self.clk_num}"

    # Acquire commands
    def set_acq_avg_state(self, state: Union[str, bool]):
        """ Set the average state of the acquired system. """
        self.write(f"acquire:average {state}")

    def set_acq_best(self, opt: str):
        self.value_check(opt.lower(), ("thr", "flat"))
        self.write(f"acquire:best {opt}")
        
    def set_acq_count(self, cnt: int):
        """ Set the count of the acquired system. """
        self.value_check(cnt, (1, 4096))
        self.write(f"acquire:count {cnt}")

    # Channel commands
    def set_bandwidth(self, setting: str):
        """ Set the channel's bandwidth. """
        self.value_check(setting.lower(), ("high", "mid", "low"))
        self.write(f"{self.channel}:bandwidth {setting}")

    def set_connector(self, connector: str):
        """ Set the channel's connector. """
        self.value_check(connector.lower(), ("a", "b"))
        self.write(f"{self.channel}:connector {connector}")

    def set_wavelength(self, wavelength: Union[str, float]):
        """ 
        Set the channel's wavelength. 
        
        Factory wavelengths: 
            - wavelength1: 8.50E-007, wavelength2: 1.31E-006, wavelength3: 1.55E-006
            - user-defined: in nm
        """
        wavelength = wavelength*1e-09
        self.write(f"{self.channel}:wavelength {wavelength}")


    # Clock recovery
    def set_clk_arelock(self, state: Union[bool, str]):
        """ Set the clock state. """
        self.write(f"{self.clock}:arelock {state}")

    def set_clk_arelock_cancel(self):
        """ Unlock the clock state. """
        self.write(f"{self.clock}:arelock:cancel")

    def set_clk_lbwmode(self, mode: str):
        """ Set the PLL's loop-bandwidth entry mode. """
        self.value_check(mode.lower(), ("fixed", "fix", "rdependent", "rdep"))
        self.write(f"{self.clock}:lbwmode {mode}")

    def set_clk_clbandwidth(self, bandwidth: float):
        """ Set the PLL's loop bandwidth. """
        # need to set LBWMode to fixed before running this cmd
        self.value_check(bandwidth, (30e+3, 20e+6))
        self.write(f"{self.clock}:clbandwidth {bandwidth}")

    def set_clk_crate(self, rate: float):
        """ Sets the input data rate. """
        self.write(f"{self.clock}:crate {rate}")

    def set_clk_autoodratio_state(self, state: bool):
        """ Set the state of automatic selection of front-panel output clock divide ratio. """
        self.write(f"{self.clock}:odratio:auto {state}")

    def set_clk_odratio(self, rdiv: str):
        """ Sets the output clock divide ratio (Recovered Clock Out). """
        self.write(f"{self.clock}:odratio {rdiv}")

    def get_clk_arelock_state(self) -> bool:
        return self.query_bool(f"{self.clock}:state?")
    
    def get_clk_freq(self) -> float:
        """ Returns frequency of recovered data clock. """
        return self.query_float(f"{self.clock}:cfrequency?")
    
    def get_clk_clbandwidth(self) -> float:
        """ Returns loop bandwidth of recovered data clock. """
        return self.query_float(f"{self.clock}:clbandwidth?")

    def get_clk_spresent(self, num: int) -> bool:
        return self.query_bool(f"{self.clock}:spresent? receiver{num}")
    


class KeysightFlexDCA(BaseInstrument):
    """
    Keysight FlexDCA for controlling 86100D Wide-Bandwidth Oscilloscope VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm: str
        Argument for resource manager (for simualated device only)
    chan: int, default = 1
        The input channel
    clk_num: int, default = 1
        The clock recovery number
    """

    def __init__(self, addr: str, rm: str="", chan: int=1, clk_num: int=1):
        super().__init__(rsc_addr=addr, rm=rm)
        self.chan = chan
        self.clk_num = clk_num
        self.channel = f"channel{chan}"
        self.clock = f"crecovery{self.clk_num}"

    def lock_clk(self):
        """ Locks clock recovery to the data rate. """
        self.write(f"{self.clock}:relock")

    def set_clk_rate(self, rate: float):
        """ Set the input signal's data rate """
        self.write(f"{self.clock}:rate {rate}")

    def set_clk_odratio(self, ratio: str):
        """
        Set the output clock divide ratio (Recovered Clock Out).

        e.g. unit: 1:1, sub2: 1:2,etc.
        """
        types = ("unit", "sub2", "sub4", "sub8", "sub16", "sub32", "sup2", "sup4", "sup8")
        self.value_check(ratio.lower(), types)
        self.write(f"{self.clock}:odratio {ratio}")

    def set_clk_adratio(self, ratio: str):
        """
        Set the auxiliary clock divide output ratio.

        e.g. sub1: 1:1, sub2: 1:2,etc.
        """
        types = ("sub1", "sub2", "sub4", "sub8", "sub16")
        self.value_check(ratio.lower(), types)
        self.write(f"{self.clock}:adratio {ratio}")

    def get_clk_odratio(self) -> str:
        """ Get the output clock divide ratio (Recovered Clock Out). """
        return self.query(f"{self.clock}:odratio?")

    def get_clk_adratio(self) -> str:
        """ Get the auxiliary clock divide ratio (Recovered Clock Out). """
        return self.query(f"{self.clock}:adratio?")

    def get_clk_lock(self) -> bool:
        """ Get the output clock lock state. """
        return self.query_bool(f"{self.clock}:locked?")
