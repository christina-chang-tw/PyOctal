from lib.base import BaseInstrument

class AmetekDSP7230(BaseInstrument):

    def __init__(self, addr: str):
        super().__init__(rsc_addr=addr)

    def get_mag(self):
        return self.query_float("mag.?")

    def get_x_volt(self):
        return self.query_float("x.?")
    
    def get_y_volt(self):
        return self.query_float("y.?")