from lib.base import BaseInstrument

class ThorlabsITC4002QCL(BaseInstrument):

    def __init__(self, addr):
        super().__init__(rsc_addr=addr)

    def get_curr(self):
        return self.query_float("source:current?")
    
    def get_curr_max(self):
        return self.query_float("source:current? max")
    
    def set_curr(self, curr):
        if curr > self.get_curr_max():
            raise RuntimeError("Current over safe maximum current")
        self.write(f"source:current {curr}")