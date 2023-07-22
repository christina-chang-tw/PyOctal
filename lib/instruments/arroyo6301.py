from lib.base import BaseInstrument
from lib.util.util import get_com_full_addr

class Arroyo6301(BaseInstrument):

    def __init__(self, addr):
        super().__init__(rsc_addr=get_com_full_addr(addr))

    def set_output_state(self, state: bool=1):
        self.write(f"output {state}")

    def set_laser_curr(self, curr: float):
        self.write(f"laser:ldi {curr}")

    def set_laser_volt(self, volt: float):
        self.write(f"laser:ldv {volt}")

    def set_laser_duty_cycles(self, dcycles: float=1):
        # set duty cycle
        self.write(f"laser:dc {dcycles}")

    def get_laser_curr(self):
        return self.query_float("laser:ldi?")
    
    