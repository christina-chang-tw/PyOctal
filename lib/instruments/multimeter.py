class Multimeter():
    def __init__(self, rm, addr: str, src_num: int, src_chan: int, sens_num: int, sens_chan: int):
        self.instr = rm.open_resource(addr)
        self.src_num = src_num
        self.src_chan = src_chan
        self.sens_num = sens_num
        self.sens_chan = sens_chan

class M_8163B:
    """
    Instrument: 8163B Lightwave Multimeter
    
    Remote control the multimeter with this library
    ** Not tested **
    """

    def __init__(self, rm, addr: str="GPIB0::25::INSTR", src_num: int=1, src_chan: int=1, sens_num: int=2, sens_chan: int=1):
        super().__init__(rm=rm, addr=addr, src_num=src_num, src_chan=src_chan, sens_num=sens_num, sens_chan=sens_chan) 

    def setup(self, wavelength: float=1550, power: float=10):
        self.instr.write("*RST")
        self.instr.write(f":sense{self.sens_num}:channel{self.sens_chan}:power:range:auto ON")
        self.instr.write(f":sense{self.sens_num}:channel{self.sens_chan}:power:unit Watt")
        self.set_wavelength(wavelength=wavelength)
        self.set_power(pow(10, power/10)/1000)
        self.set_average_time(period=200e-03) # avgtime = 200ms
        self.set_unit(source="dBm", sensor="Watt")
        self.switch_laser_state(1)


    def set_average_time(self, period):
        self.instr.write(f":sense{self.sens_num}:channel{self.sens_chan}:power:atime {period}s")

    def _set_sens_wavelength(self, wavelength: float):
        self.instr.write(f":sense{self.sens_num}:channel{self.sens_chan}:power:wavelength {wavelength}")

    def _set_src_wavelength(self, wavelength: float):
        self.instr.write(f":source{self.src_num}:channel{self.src_chan}:wavelength:fixed {wavelength}")

    # Setting the detector
    def set_power_range(self, prange: float): # in dBm
        self.instr.write(f":sense{self.sens_num}:channel{self.sens_chan}:power:range {prange}dBm")

    def set_power_range_auto(self, auto: bool):
        self.instr.write(f":sense{self.sens_num}:channel{self.sens_chan}:power:range:auto {auto}")

    def read_power(self):
        return self.instr.query(f":read{self.sens_num}:channel{self.sens_chan}:power:dc?")

    # Setting the source
    def set_unit(self, source: str="dBm", sensor: str="Watt"):
        self.instr.write(f":power:unit {source}") # set the source unit in dBm
        self.instr.write(f":sense:power:unit {sensor}") # set sensor unit

    def set_wavelength(self, wavelength: float):
        wavelength = wavelength * 1e-09
        self._set_sens_wavelength(wavelength)
        self._set_src_wavelength(wavelength)

    def switch_laser_state(self, status: bool):
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:power:state {status}")

    def set_power(self, power: float):
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:power:level:immediate:amplitude {power}dBm")

    # Setting source sweep parameters
    def set_sweep_mode(self, mode: str="STEP"): # STEP, MAN, CONT
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:sweep:mode {mode}")

    def set_sweep_start_stop(self, start: float, stop: float):
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:start {start}nm")
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:stop {stop}nm")

    def set_sweep_state(self, state: int): # 0 - stop, 1 - start, 2 - pause, 3 - continue
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:state {state}")
    
    def set_sweep_step(self, width: float):
        self.instr.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:step {width}nm")
    