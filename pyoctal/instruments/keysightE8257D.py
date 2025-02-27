from typing import Union

from pyvisa import ResourceManager

from pyoctal.instruments.base import BaseInstrument

class KeysightE8257D(BaseInstrument):
    """
    Keysight E8257D PSG Signal Geneartors VISA Libray.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """

    def __init__(self, rm: ResourceManager):
        super().__init__(rm=rm)

    # Correction subsystem
    def load_corr_file(self, fname: str):
        """ Load correction file. """
        self.write(f"correction:flatness:load {fname}")

    def set_corr_state(self, state: Union[bool, str]):
        """ Set correction system state. """
        self.write(f"correction:state {state}")
        
    def get_corr_flat_points(self) -> float:
        """ Get correction flatness points. """
        return self.query_float("correction:flatness:points?")
    

    def set_freq_fixed(self, freq: float):
        """ Set fixed frequency [GHz]. """
        self.write(f"frequency:fixed {freq}GHz")

    def set_freq_cw(self, freq: float):
        """ Set continuous waveform frequency [GHz]. """
        self.write(f"frequency:cw {freq}GHz")

    def set_freq_offset(self, foffset: float):
        """ Set frequency offset [GHz]. """
        self.value_check(foffset, (-200e+9, 200e+9))
        self.write(f"frequency:offset {foffset}GHz")

    def set_freq_mode(self, mode: str):
        """ Set frequency mode. """
        self.value_check(mode.lower(), ("fixed", "fix", "cw", "sweep", "swe", "list"))
        self.write(f"frequency:mode {mode}")

    def set_freq_span(self, span: float):
        """ Set frequency span [GHz]. """
        self.write(f"frequency:span {span}GHz")

    def set_freq_start(self, fstart: float):
        """ Set starting frequency [GHz]. """
        self.write(f"frequency:start {fstart}GHz")

    def set_freq_stop(self, fstop: float):
        """ Set stopping frequency [GHz]. """
        self.write(f"frequency:stop {fstop}GHz")
    
    def set_center_freq(self, freq: float):
        """ Set center frequency [GHz]. """
        self.write(f"frequency:center {freq}GHz")

    def set_freq_channel_state(self, state: Union[bool, str]):
        """ Set the state of each frequency channel. """
        self.write(f"frequency:channels:state {state}")

    def get_freq_fixed(self) -> float:
        """ Get the fixed frequency. """
        return self.query_float("frequency:fixed?")
    
    def get_freq_cw(self) -> float:
        """ Get the continuous waveform frequency. """
        return self.query_float("frequency:cw?")

    def get_freq_mode(self) -> str:
        """ Get the mode of the frequency system. """
        return self.query("frequency:mode?")

    # Power 
    def set_output_power(self, power: float):
        """ Get the output power [dBm]. """
        self.write(f"power:level:immediate:amplitude {power}dBm")