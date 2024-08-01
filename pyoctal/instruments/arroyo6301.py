from pyvisa import ResourceManager

from pyoctal.instruments.base import BaseInstrument

class Arroyo6301(BaseInstrument):
    """
    Arroyo 6301 ComboSource VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """

    def __init__(self, addr: str, rm: ResourceManager):
        super().__init__(rsc_addr=addr, rm=rm)

    def set_output_state(self, state: bool):
        """ Set the laser output state. """
        self.write(f"output {state}")

    def set_laser_curr(self, curr: float):
        """ Set the laser current [A]. """
        self.write(f"laser:ldi {curr}")

    def set_laser_volt(self, volt: float):
        """ Set the laser voltage [V]. """
        self.write(f"laser:ldv {volt}")

    def set_laser_duty_cycles(self, dcycles: float):
        """ Set the laser duty cycles. """
        self.write(f"laser:dc {dcycles}")

    def get_laser_curr(self) -> float:
        """ Set the laser current [A]. """
        return self.query_float("laser:ldi?")
