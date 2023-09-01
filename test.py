import pyvisa

from pyoctal.instruments import FiberlabsAMP

rm = pyvisa.ResourceManager()

amp = FiberlabsAMP(addr="GPIB0::1::INSTR", rm=rm, read_termination="")

amp.set_output_state(0)