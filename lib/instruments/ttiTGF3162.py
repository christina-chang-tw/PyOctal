from lib.base import BaseInstrument
from lib.error import *

from typing import Union
import numpy as np

class TTiTGF3162(BaseInstrument):
    """
    TTi TGF3162 Dual Channel Arbitrary Function Generator

    Parameters
    ----------
    addr: str
        The address of the instrument
    """

    def __init__(self, addr: str):
        super().__init__(rsc_addr=addr)

    def set_freq(self, freq: float):
        self.write(f"frequency {freq}") # Hz

    def set_ampl(self, ampl: float):
        self.write(f"ampl {ampl}")

    def set_ampl_lolvl(self, lolvl: float):
        # set amplitude low level
        self.write(f"lolvl {lolvl}")

    def set_ampl_hilvl(self, hilvl: float):
        # set amplitude high level
        self.write(f"hilvl {hilvl}")

    def set_dc_offset(self, offset: float):
        self.write(f"dcoffs {offset}")

    def set_zload(self, zload: Union[str, float]):
        self.write(f"zload {zload}")

    def set_output_state(self, state: str):
        self.value_check(state.lower(), ("on", "off", "normal", "invert"))
        self.write(f"output {state}")

    def select_channel(self, channel: int):
        # set the channel as the destination of the
        # subsequent cmds
        self.value_check(channel, (1, 2))
        self.write(f"chn {channel}")

    def load_arb(self, memchan):
        self.write(f"arbload arb{memchan}")

    def set_arb_waveform(self, array, memchan):
        # the array of values should be between -1 and 1
        # max length = 1024
        values = np.int16(array*pow(2, 15))
        self.write_binary_values(f"arb{memchan} ", values, is_big_endian=True, datatype='h')

    def set_arb_output(self):
        self.write("wave arb")

    def set_arb_dc(self, memchan):
        y = 0.999*np.ones(2)
        self.set_arb_waveform(y, memchan)

    def get_arb_waveform(self, memchan):
        return self.query_binary_values(f"arb{memchan}?")