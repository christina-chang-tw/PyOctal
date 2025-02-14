import sys
from time import time
from typing import List

from pyvisa import ResourceManager

from pyoctal.instruments.base import BaseInstrument

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

    def __init__(self, rm: ResourceManager):
        super().__init__(rm=rm)

    def setup(self, voltage: float, current: float):
        self.reset()
        self.set_output_state(state=1)
        self.set_params(voltage, current)
        
    def disconnect(self):
        self.write("display on")

    def set_output_state(self, state: bool):
        """ Set the voltage output state. """
        self.write(f"output {state}")

    def set_volt(self, volt: float):
        """ Set the DC voltage [V]. """
        self.write(f"voltage {volt}")

    def set_curr(self, curr: float):
        """ Set the DC current [A]. """
        self.write(f"current {curr}")

    def set_params(self, volt: float, curr: float):
        """ Set the DC voltage [V] and current [A]. """
        self.write(f"apply {volt} , {curr}")
        
    def set_volt_range(self, vrange: str):
        """ Set the voltage range. LOW or HIGH"""
        self.write(f"voltage:range {str(vrange.upper())}")
        
    def set_curr_range(self, crange: str):
        """ Set the current range. LOW or HIGH"""
        self.write(f"current:range {str(crange.upper())}")

    def get_output_state(self) -> bool:
        """ Get the DC output state. """
        return self.query_bool("output?")

    def get_params(self) -> List: # return [volt, curr]
        """ Get the DC voltage [V] and current [A]. """
        params = self.query("apply?").split(",") # split the str up by ,
        params = [float(i.replace('"', '')) for i in params]
        return params

    def get_curr(self) -> float:
        """ Get the DC current [A]. """
        return self.query_float("measure:current?")

    def get_volt(self) -> float:
        """ Get the DC voltage [V]. """
        return self.query_float("measure:voltage?")
    
    def get_curr_max(self) -> float:
        """ Get the maximum current [A]. """
        return self.query_float("current? max")
    
    def get_volt_max(self) -> float:
        """ Get the maximum voltage [V]. """
        return self.query_float("voltage? max")


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
            if time() - start_time > max_time:
                sys.exit("Timeout: Current did not stabilize.")
            prev_curr = curr
