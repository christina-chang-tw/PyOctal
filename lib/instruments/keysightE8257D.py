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

    def __init__(self, addr):
        super().__init__(rsc_addr=addr)

    # Correction subsystem
    def load_corr_file(self, fname: str):
        self.write(f"correction:flatness:load {fname}")

    def set_corr_state(self, state: Union[bool, str]):
        self.write(f"correction:state {state}")
        
    def get_corr_flat_points(self):
        return self.query_float("correction:flatness:points")
    
    # Frequency subsystem (everything is in GHz)
    def set_freq_fixed(self, freq: float):
        self.write(f"frequency:fixed {freq}GHz")

    def set_freq_cw(self, freq: float):
        self.write(f"frequency:cw {freq}GHz")

    def set_freq_offset(self, foffset: float):
        if not -200e+09 < foffset < 200e+09:
            raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
        self.write(f"frequency:offset {foffset}GHz")

    def set_freq_mode(self, mode: str):
        if mode.lower() not in ("fixed", "fix", "cw", "sweep", "swe", "list"):
            raise  ValueError(f"Error code {PARAM_INVALID_ERR:x}: {error_message[PARAM_INVALID_ERR]}")
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

    def get_freq_fixed(self):
        return self.query(f"frequency:fixed?")
    
    def get_freq_cw(self):
        return self.query(f"frequency:cw?")

    def get_freq_mode(self):
        return self.query(f"frequency:mode?")

    # Power 
    def set_output_power(self, power: float):
        self.write(f"power:level:immediate:amplitude {power}dBm")