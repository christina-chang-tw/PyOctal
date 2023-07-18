from lib.instruments.base import BaseInstrument

class AgilentE3640A(BaseInstrument):
    """
    Instrument: E3640A Power Meter
    
    Remote control the power meter with this library
    ** Not tested **
    """

    def __init__(self, addr: str="GPIB0::4::INSTR"):
        super().__init__(rsc_addr=addr) 

    def setup(self):
        self.instr.write("*RST")
        self.set_output_status(1)

    def set_volt(self, volt: float):
        self.write(f"voltage {volt}")
    
    def set_current(self, curr: float):
        self.write(f"current {curr}")

    def set_params(self, volt: float, cur: float):
        self.write(f"apply {volt}, {cur}")

    def read_params(self):
        return self.query("apply?")

    def read_current(self):
        return self.query("measure:current?")
    
    def read_voltage(self):
        return self.query("measure:voltage?")
    
    def set_output_status(self, status: bool):
        self.write(f"output {status}")


if __name__ == "__main__":
    power_meter = AgilentE3640A()
    power_meter.set_output_status(1)
    power_meter.set_volt(3)
    power_meter.set_current(1)
    power_meter.set_params(volt=4, cur=2)
    ans = power_meter.read_voltage()
    print(ans)