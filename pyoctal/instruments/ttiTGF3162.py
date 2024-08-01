from typing import Union, List, Tuple
import numpy as np

from pyoctal.instruments.base import BaseInstrument
from pyoctal.utils.error import *

class TTiTGF3162(BaseInstrument):
    """
    TTi TGF3162 Dual Channel Arbitrary Function Generator VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """

    def __init__(self, addr: str, rm):
        super().__init__(rsc_addr=addr, rm=rm)

    def set_freq(self, freq: float):
        """ Set frequency in Hz. """
        self.write(f"frequency {freq}") # Hz

    def set_ampl(self, ampl: float):
        """ Set amplitude. """
        self.write(f"ampl {ampl}")

    def set_ampl_lolvl(self, lolvl: float):
        """ Set amplitude low level. """
        self.write(f"lolvl {lolvl}")

    def set_ampl_hilvl(self, hilvl: float):
        """ Set amplitude high level. """
        self.write(f"hilvl {hilvl}")

    def set_dc_offset(self, offset: float):
        """ Set DC offset. """
        self.write(f"dcoffs {offset}")

    def set_zload(self, zload: Union[str, float]):
        self.write(f"zload {zload}")

    def set_output_state(self, state: str):
        """ Set output state. """
        self.value_check(state.lower(), ("on", "off", "normal", "invert"))
        self.write(f"output {state}")

    def select_channel(self, channel: int):
        """ Set the channel as the destination of the subsequent cmds. """
        self.value_check(channel, (1, 2))
        self.write(f"chn {channel}")

    def load_arb(self, memchan: int):
        """ Load arbitrary waveform. """
        self.write(f"arbload arb{memchan}")

    def set_arb_waveform(self, array: Union[List, Tuple], memchan: int):
        """ 
        Set arbitrary waveform.
        
        The array of values should be between -1 and 1 and the max length is 1024.
        """
        values = np.int16(array*pow(2, 15))
        self.write_binary_values(f"arb{memchan}, {values}", is_big_endian=True, datatype='h')

    def set_arb_output(self):
        """ Set the waveform output to arbitrary. """
        self.write("wave arb")

    def set_arb_dc(self, memchan: int):
        """ Set the arbitrary waveform dc. """
        y = 0.999*np.ones(2)
        self.set_arb_waveform(y, memchan)

    def get_arb_waveform(self, memchan: int) -> Union[List,Tuple]:
        """ Get the arbitrary waveform. """
        return self.query_binary_values(f"arb{memchan}?")