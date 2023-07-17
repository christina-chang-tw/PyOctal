class AgilentE3640A:
    """
    Instrument: E3640A Power Meter
    
    Remote control the power meter with this library
    ** Not tested **
    """

    def __init__(self, rm, addr: str="GPIB0::28::INSTR"):
        self.instr = rm.open_resource(addr)

    def setup(self):
        self.instr.write("*RST")
        self.set_output_status(1)

    def set_volt(self, volt: float):
        self.instr.write(f"voltage {volt}")
    
    def set_current(self, curr: float):
        self.instr.write(f"current {curr}")

    def set_params(self, volt: float, curr: float):
        self.instr.write(f"apply {volt}, {curr}")

    def read_params(self):
        return self.instr.query("apply?")

    def read_current(self):
        return self.instr.query("measure:current?")
    
    def read_voltage(self):
        return self.instr.query("measure:voltage?")
    
    def set_output_status(self, status: bool):
        self.instr.write(f"output {status}")

    def close(self):
        self.instr.close()