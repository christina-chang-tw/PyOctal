import time
from typing import Union, List, Tuple

from pyvisa import ResourceManager

from pyoctal.instruments.base import BaseInstrument
from pyoctal.utils.error import PARAM_INVALID_ERR, error_message

class AmetekDSP7230(BaseInstrument):
    """
    Ametek DSP7230 DSP Lock-In Amplifier VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """

    def __init__(self, rm: ResourceManager):
        super().__init__(rm=rm)

    def get_mag(self) -> float:
        """ Get the magnitude. """
        return self.query_float("mag.?")

    def get_x_volt(self) -> float:
        """ Get the module x voltage. """
        return self.query_float("x.?")

    def get_y_volt(self) -> float:
        """ Get the module y voltage. """
        return self.query_float("y.?")

class AmetekDSP7265(BaseInstrument):
    """
    Ametek DSP7265 DSP Lock-In VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """

    def __init__(self, addr: str, rm):
        super().__init__(rsc_addr=addr, rm=rm)

    # Set
    def set_mag(self, mag: float):
        """ Get the magnitude. """
        self.write(f"mag {mag}")

    def set_mag1(self, mag: float):
        """ Get the magnitude of module 1. """
        self.write(f"mag1 {mag}")

    def set_mag2(self, mag: float):
        """ Get the magnitude of module 2. """
        self.write(f"mag2 {mag}")

    def set_osc(self, freq: float):
        """ Set the frequency. """
        self.write(f"of {freq}")

    def set_user_eq(self, eq: str):
        """ Set the equation. """
        if not isinstance(eq, Union[List, Tuple]):
            raise ValueError(
                f"Error code {PARAM_INVALID_ERR:x}: \
                {error_message[PARAM_INVALID_ERR]}. Param should be a list"
            )
        self.write(f'defequ {" ".join(eq)}')

    def set_dual_tc(self, tc: int):
        tconst_dict = {
        #   time constant (ms) : n
            5: 7,
            10: 8,
            20: 9,
            50: 10,
            1e+2: 11, # 100
            2e+2: 12,
            5e+2: 13,
            1e+3: 14, # 1000
            2e+3: 15,
            5e+3: 16,
            1e+4: 17, # 10000
            2e+4: 18,
        }

        n = tconst_dict[tc]
        # set both channels to the same time constant
        self.write(f"tc1 {n}")
        self.write(f"tc2 {n}")

    def set_dual_sensitivity(self, sens: int):
        sens_dict = {
        #   sensitivity [mV] : n
            1: 18,
            2: 19,
            5: 20,
            10: 21,
            20: 22,
            50: 23,
            1e+2: 24, # 100
            2e+2: 25,
            5e+2: 26,
            1e+3: 27, # 1000
        }

        n = sens_dict[sens]
        # set both channels to the same sensitivity
        self.write(f"sen1 {n}")
        self.write(f"sen2 {n}")

    def set_dual_slope(self, slope: int):
        slope_dict = {
        #   slope : n
            6: 0,
            12: 1,
            18: 2,
            24: 3,
        }

        n = slope_dict[slope]
        self.write(f"sen1 {n}")
        self.write(f"sen2 {n}")


    # get
    def get_mag(self) -> float:
        """ Get the magnitude. """
        return self.query_float("mag.?")

    def get_mag1(self) -> float:
        """ Get the magnitude of module 1. """
        return self.query_float("mag1.?")

    def get_mag2(self) -> float:
        """ Get the magnitude of module 2. """
        return self.query_float("mag2.?")

    def get_eq1(self) -> float:
        """ Get the equation 1. """
        return self.query_float("equ1.?")

    def get_avgv_ch(self, chan: int, duration: float, wait: float) -> float:
        """ Obtain the averaged voltage value of a channel """
        points = int(duration/wait)
        v_sum = 0
        func = None

        # get the correct function to call
        if chan == 1:
            func = self.get_mag1
        elif chan == 2:
            func = self.get_mag2

        for _ in range(points):
            time.sleep(wait)
            volt = func()
            v_sum = v_sum + volt

        return v_sum/points
