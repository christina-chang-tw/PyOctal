from lib.base import BaseInstrument


class AgilentE3640A(BaseInstrument):
    """
    Instrument: E3640A Power Meter
    
    Remote control the power meter with this library
    """

    def __init__(self, addr: str="GPIB0::4::INSTR"):
        super().__init__(rsc_addr=addr) 

    def setup(self):
        self.reset()
        self.set_output_status(status=1)

    def set_volt(self, volt: float=0):
        self.write(f"voltage {volt}")
    
    def set_curr(self, curr: float=0):
        self.write(f"current {curr}")

    def set_params(self, volt: float=0, curr: float=0):
        self.write(f"apply {volt}, {curr}")

    def read_params(self):
        return self.query("apply?")

    def read_curr(self):
        return self.query("measure:current?")
    
    def read_volt(self):
        return self.query("measure:voltage?")
    
    def set_output_status(self, status: bool=1):
        self.write(f"output {status}")