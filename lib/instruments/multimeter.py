import pyvisa

c = 299792458

class M_8163B:

    def __init__(self, src_num: int=1, src_chan: int=1, sens_num: int=1, sens_chan: int=1):
        self.instr = []
        self.src_num = src_num
        self.src_chan = src_chan
        self.sens_num = sens_num
        self.sens_chan = sens_chan

    def setup(self, rm, addr: str="GPIB0::28::INSTR"):
        self.instr = rm.open_resource(addr)
        self.instr.write("*RST")
        self.instr.write(f"sense{self.sens_num}:channel{self.sens_num}:power:range:auto ON")
        self.instr.write(f"sense{self.sens_num}:channel{self.sens_num}:power:unit Watt")
        self.switch_laser_state(1)

    def _set_sens_wavelength(self, wavelength: float):
        self.instr.write(f"sense{self.sens_num}:channel{self.sens_num}:power:wavelength {wavelength}")

    def _set_src_wavelength(self, wavelength: float):
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:power:wavelength {wavelength}")

    # Setting the detector
    def set_power_range(self, prange: float): # in dBm
        self.instr.write(f"sense{self.sens_num}:channel{self.sens_chan}:power:range {prange}")

    def set_power_range_auto(self, auto: bool):
        self.instr.write(f"sense{self.sens_num}:channel{self.sens_chan}:power:range:auto {auto}")

    # Reading off the detector
    def read_status(self):
        return self.instr.query(":status:operation:condition?")

    def read_power(self):
        return self.instr.query(f":read{self.sens_num}:channel{self.sens_chan}:power:dc?")

    def read_sweep_result(self):
        return self.instr.query(f":sense:channel{self.sens_chan}:function:result:block?")

    # Setting the source
    def set_unit(self, unit):
        self.instr.write(f":read{self.sens_num}:channel{self.sens_num}:power:unit {unit}")

    def set_wavelength(self, wavelength: float):
        self._set_sens_wavelength(wavelength)
        self._set_src_wavelength(wavelength)

    def switch_laser_state(self, status: bool):
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:state {status}")

    def set_power(self, power: float):
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:power:level:immediate:amplitude {power}")

    # Setting source sweep parameters
    def set_sweep_mode(self, mode: str): # STEP, MAN, CONT
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:sweep:mode {mode}")

    def set_sweep_start_stop(self, start: float, stop: float):
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:start {start}nm")
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:stop {stop}nm")

    def set_sweep_state(self, state: int): # 0 - stop, 1 - start, 2 - pause, 3 - continue
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:state {state}")
    
    def set_sweep_step(self, width: float):
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:step {width}nm")
    