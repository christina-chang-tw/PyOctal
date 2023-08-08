from lib.base import BaseInstrument
from lib.error import *

import time
from typing import Tuple

class Keithley2400(BaseInstrument):
    """
    Keithley 2400 Source Measure Unit VISA Library

    Parameters
    ----------
    addr: str
        The address of the instrument
    """
    
    def __init__(self, addr: str):
         super().__init__(rsc_addr=addr)

    def initiate(self):
        self.write(f"initiate")

    def meas_curr(self) -> float:
        data = self.query("measure:current?")
        return float(data.split(",")[1])

    def meas_volt(self) -> float:
        data = self.query("measure:voltage?")
        return float(data.split(",")[0])
    

    # Detector
    def set_detect_vlim(self, volt: float):
        self.value_check(volt, (-210.0, 210.0))
        self.write(f"sense:voltage:protection {volt}")

    def set_detect_ilim(self, curr: float):
        self.value_check(curr, (-1.05, 1.05))
        self.write(f"sense:current:protection {curr}")

    def set_detect_npl_cycles(self, speed: float):
        self.write(f"sense:current:nplcycles {speed}")

    def get_detect_vlim(self) -> float:
        return self.query_float("sense:voltage:protection?")
    
    def get_detect_ilim(self) -> float:
        return self.query_float("sense:current:protection?")
    
    

    # Laser
    def set_laser_state(self, state: bool=1):
        self.write(f"output:state {state}")

    def set_laser_mode(self, mode: str):
        self.value_check(mode.lower(), ("curr", "volt", "mem"))
        self.write(f"source:function {mode}")

    def set_laser_volt(self, volt):
        self.value_check(volt, (-210.0, 210.0))
        self.write(f"source:voltage:level {volt}")

    def set_laser_curr(self, curr):
        self.value_check(curr, (-1.05, 1.05))
        self.write(f"source:current:level {curr}")

    def get_laser_mode(self) -> str:
        return self.query("source:function?")

    def get_laser_volt(self) -> float:
        return self.query_float("source:voltage:level?")
    
    def get_laser_curr(self) -> float:
        return self.query_float("source:current:level?")

    
    # Trace
    def set_trace_source(self, source: str):
        self.write(f"trace:feed {source}")
    
    def set_trace_points(self, pts: int):
        self.write(f"trace:points {pts}")

    def set_trace_ctl(self, ctl: str):
        self.value_check(ctl.lower(), ("never", "next"))
        self.write(f"trace:feed:control {ctl}")

    def get_trace_data(self):
        return self.query("trace:data?")


    # Trigger
    def set_trig_count(self, count: int):
        self.value_check(count, (1, 2500))
        self.write(f"trigger:count {count}")


    # Calculate
    def set_calc3_format(self, format: str="mean"):
        self.value_check(format.lower(), ("mean", "sdev", "max", "min", "pkpk"))
        self.write(f"calculate3:format {format}")

    def get_calc3_data(self):
        return self.query("calculate3:data?")
		

    # Complex functions
    def meas_curr_buf(self, volt: float, n, speed) -> Tuple[list, float]:
        """ measure current buffer """
        self.set_laser_volt(volt=volt)
        self.set_detect_npl_cycles(speed=speed)
        self.set_trace_source(source="sense")
        self.set_trace_points(pts=n)
        self.set_trace_ctl(ctl="next")
        self.set_trig_count(count=n)
        self.set_laser_state(1)
        self.initiate()
        
        time.sleep(0.1+1*speed+speed*n*0.06)
        trace_data = self.get_trace_data()
        self.set_calc3_format(format="mean")

        calc3_data = self.get_calc3_data()
        self.set_trace_ctl(ctl="never")

        currents = [float(trace_data.split(","[5*(i-1)+1])) for i in range(n)]
        current = calc3_data.split(",")[1]
        
        return currents, current