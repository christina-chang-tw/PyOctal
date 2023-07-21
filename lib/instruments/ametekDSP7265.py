from lib.base import BaseInstrument

import time
from typing import Union

class AmetekDSP7230(BaseInstrument):

    def __init__(self, addr: str):
        super().__init__(rsc_addr=addr)


    # Set
    def set_mag(self, mag: float):
        self.write(f"mag {mag}")

    def set_mag1(self, mag: float):
        self.write(f"mag1 {mag}")

    def set_mag2(self, mag: float):
        self.write(f"mag2 {mag}")

    def set_osc(self, freq: float):
        self.write(f"of. {freq}")
    
    def set_user_eq(self, eq: str):
        if not isinstance(eq, Union[list, tuple]):
            raise RuntimeError("Bad value: equation should be a list")
        self.write(f'defequ {[" ".join(i) for i in eq]}')

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
    def get_mag(self):
        return self.query_float("mag.?")

    def get_mag1(self):
        return self.query_float("mag1.?")
    
    def get_mag2(self):
        return self.query_float("mag2.?")
    
    def get_eq1(self):
        return self.query_float("equ1.?")


    
    def avg_channel1(self, duration: float, wait: float):
        points = int(duration/wait)
        v_sum = 0

        for _ in range(points):
            time.sleep(wait)
            volt = self.get_mag1()
            v_sum = v_sum + volt

        return v_sum/points


