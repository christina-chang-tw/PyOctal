from octal.base import BaseInstrument

class Arroyo6301(BaseInstrument):
    """
    Arroyo 6301 ComboSource VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    """

    def __init__(self, addr: str):
        super().__init__(rsc_addr=addr)

    def set_output_state(self, state: bool):
        self.write(f"output {state}")

    def set_laser_curr(self, curr: float):
        self.write(f"laser:ldi {curr}")

    def set_laser_volt(self, volt: float):
        self.write(f"laser:ldv {volt}")

    def set_laser_duty_cycles(self, dcycles: float):
        # set duty cycle
        self.write(f"laser:dc {dcycles}")

    def get_laser_curr(self) -> float:
        return self.query_float("laser:ldi?")
    
    