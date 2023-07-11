from lib.instruments.multimeter import M_8163B

import pyvisa

if __name__ == "__main__":
    rm = pyvisa.ResourceManager()
    instr = M_8163B()
    instr.setup(rm=rm)
    instr.set_wavelength(wavelength=1550)
    instr.close()
    rm.close()
