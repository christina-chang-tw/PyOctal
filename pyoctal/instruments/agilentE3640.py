from pyoctal.instruments.base import BaseInstrument
import sys
from time import time

class AgilentE3640A(BaseInstrument):
    """
    Agilent E3640A Power Meter VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """

    def __init__(self, addr: str, rm):
        super().__init__(rsc_addr=addr, rm=rm)

    def setup(self):
        self.reset()
        self.set_output_state(state=1)

    def set_output_state(self, state: bool):
        """ Set the laser output state. """
        self.write(f"output {state}")

    def set_volt(self, volt: float):
        """ Set the laser voltage [V]. """
        self.write(f"voltage {volt}")
    
    def set_curr(self, curr: float):
        """ Set the laser current [A]. """
        self.write(f"current {curr}")

    def set_params(self, volt: float, curr: float):
        """ Set the laser voltage [V] and current [A]. """
        self.write(f"apply {volt} , {curr}")

    def get_output_state(self) -> bool:
        """ Get the laser output state. """
        return self.query_bool("output?")

    def get_params(self) -> list: # return [volt, curr]
        """ Get the laser voltage [V] and current [A]. """
        params = self.query("apply?").split(",") # split the str up by ,
        params = [float(i.replace('"', '')) for i in params]
        return params

    def get_curr(self) -> float:
        """ Get the laser current [A]. """
        return self.query_float("measure:current?")

    def get_volt(self) -> float:
        """ Get the laser voltage [V]. """
        return self.query_float("measure:voltage?")
    
    def wait_until_stable(self, tol: float=0.0008, max_time: float=20) -> None:
        """ 
        Wait until the current is stable. 
        
        Parameters
        ----------
        tol: float
            The tolerance for the current to be stable.
        max_time: float
            The maximum time to wait for the current to be stable.
        """
        start_time = time()
        prev_curr = self.get_curr()
        while True:
            curr = self.get_curr()
            if abs(curr - prev_curr) <= tol:
                break
            elif time() - start_time > max_time:
                sys.exit("Timeout: Current did not stabilize.")
            prev_curr = curr