import pyvisa

c = 299792458

class M_8163B:

    def __init__(self):
        self.instr = []

    def setup(self, rm, addr: str="GPIB0::28::INSTR"):
        self.instr = rm.open_resource(addr)
        self.instr.write("*RST")
        self.instr.write("sense:channel:power:range:auto ON")
        self.instr.write("sense:channel:power:unit Watt")
        self.switch_laser_state(1)

    def _set_sens_wavelength(self, wavelength: float):
        self.instr.write(f"sense:channel:power:wavelength {wavelength}")

    def _set_src_wavelength(self, wavelength: float):
        self.instr.write(f"source:channel:power:wavelength {wavelength}")

    def read_status(self):
        return self.instr.query(":status:operation:condition")

    def read_power(self, i, chan: int):
        return self.instr.query(f":read{i}:channel{chan}:power:dc")

    def set_unit(self, unit):
        self.instr.write(f":sense:channel:power:unit {unit}")

    def set_wavelength(self, wavelength: float):
        self._set_sens_wavelength(wavelength)
        self._set_src_wavelength(wavelength)

    def switch_laser_state(self, status: bool):
        self.instr.write(f"source:channel:state {status}")

    def set_power(self, power: float):
        self.instr.write(f"source:channel:power:level:immediate:amplitude {power}")
    
    
    