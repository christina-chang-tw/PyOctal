from lib.base import BaseInstrument
from lib.error import *

from typing import Union

class KeysightE8257D(BaseInstrument):
    """
    Keysight E8257D PSG Signal Geneartors VISA Libray

    Parameters
    ----------
    addr: str
        The address of the instrument
    """

    def __init__(self, addr: str):
        super().__init__(rsc_addr=addr)

    # Correction subsystem
    def load_corr_file(self, fname: str):
        self.write(f"correction:flatness:load {fname}")

    def set_corr_state(self, state: Union[bool, str]):
        self.write(f"correction:state {state}")
        
    def get_corr_flat_points(self) -> float:
        return self.query_float("correction:flatness:points?")
    
    # Frequency subsystem (everything is in GHz)
    def set_freq_fixed(self, freq: float):
        self.write(f"frequency:fixed {freq}GHz")

    def set_freq_cw(self, freq: float):
        self.write(f"frequency:cw {freq}GHz")

    def set_freq_offset(self, foffset: float):
        self.value_check(foffset, (-200e+9, 200e+9))
        self.write(f"frequency:offset {foffset}GHz")

    def set_freq_mode(self, mode: str):
        self.value_check(mode.lower(), ("fixed", "fix", "cw", "sweep", "swe", "list"))
        self.write(f"frequency:mode {mode}")

    def set_freq_span(self, span: float):
        self.write(f"frequency:span {span}GHz")

    def set_freq_start(self, fstart: float):
        self.write(f"frequency:start {fstart}GHz")

    def set_freq_stop(self, fstop: float):
        self.write(f"frequency:stop {fstop}GHz")
    
    def set_center_freq(self, freq: float):
        self.write(f"frequency:center {freq}GHz")

    def set_freq_channel_state(self, state: Union[bool, str]):
        self.write(f"frequency:channels:state {state}")

    def get_freq_fixed(self) -> float:
        return self.query_float(f"frequency:fixed?")
    
    def get_freq_cw(self) -> float:
        return self.query_float(f"frequency:cw?")

    def get_freq_mode(self) -> str:
        return self.query(f"frequency:mode?")

    # Power 
    def set_output_power(self, power: float):
        self.write(f"power:level:immediate:amplitude {power}dBm")