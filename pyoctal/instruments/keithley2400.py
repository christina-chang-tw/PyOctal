import time
from typing import Tuple, List

from pyvisa import ResourceManager

from pyoctal.instruments.base import BaseInstrument
from pyoctal.utils.error import *

class Keithley2400(BaseInstrument):
    """
    Keithley 2400 Source Measure Unit VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """
    
    def __init__(self, rm: ResourceManager):
         super().__init__(rm=rm)

    def initiate(self):
        """ Initiate a measurement. """
        self.write("initiate")

    def meas_curr(self) -> float:
        """ Measure current. """
        data = self.query("measure:current?")
        return float(data.split(",")[1])

    def meas_volt(self) -> float:
        """ Measure voltage. """
        data = self.query("measure:voltage?")
        return float(data.split(",")[0])
    

    # Detector
    def set_detect_vlim(self, volt: float):
        """ Set detector's voltage limit. """
        self.value_check(volt, (-210.0, 210.0))
        self.write(f"sense:voltage:protection {volt}")

    def set_detect_ilim(self, curr: float):
        """ Set detector's current limit. """
        self.value_check(curr, (-1.05, 1.05))
        self.write(f"sense:current:protection {curr}")

    def set_detect_npl_cycles(self, speed: float):
        """ Set detector's cycles. """
        self.write(f"sense:current:nplcycles {speed}")

    def get_detect_vlim(self) -> float:
        """ Get detector's voltage limit. """
        return self.query_float("sense:voltage:protection?")
    
    def get_detect_ilim(self) -> float:
        """ Get detector's current limit. """
        return self.query_float("sense:current:protection?")
    
    

    # Laser
    def set_laser_state(self, state: bool):
        """ Set laser output state. """
        self.write(f"output:state {state}")

    def set_laser_mode(self, mode: str):
        """ Set laser mode. """
        self.value_check(mode.lower(), ("curr", "volt", "mem"))
        self.write(f"source:function {mode}")

    def set_laser_volt(self, volt: float):
        """ Set laser voltage. """
        self.value_check(volt, (-210.0, 210.0))
        self.write(f"source:voltage:level {volt}")

    def set_laser_curr(self, curr: float):
        """ Set laser current. """
        self.value_check(curr, (-1.05, 1.05))
        self.write(f"source:current:level {curr}")

    def get_laser_mode(self) -> str:
        """ Get laser mode. """
        return self.query("source:function?")

    def get_laser_volt(self) -> float:
        """ Get laser voltage. """
        return self.query_float("source:voltage:level?")
    
    def get_laser_curr(self) -> float:
        """ Get laser current. """
        return self.query_float("source:current:level?")

    
    # Trace
    def set_trace_source(self, source: str):
        """ Set the source of the trace. """
        self.write(f"trace:feed {source}")
    
    def set_trace_points(self, pts: int):
        """ Set number of trace points. """
        self.write(f"trace:points {pts}")

    def set_trace_ctl(self, ctl: str):
        """ Set trace control. """
        self.value_check(ctl.lower(), ("never", "next"))
        self.write(f"trace:feed:control {ctl}")

    def get_trace_data(self):
        """ Get data from the trace. """
        return self.query("trace:data?")


    # Trigger
    def set_trig_count(self, count: int):
        """ Set trigger count. """
        self.value_check(count, (1, 2500))
        self.write(f"trigger:count {count}")


    # Calculate
    def set_calc3_format(self, calc3_fm: str):
        """ Set the format of internal calculate 3 module. """
        self.value_check(calc3_fm.lower(), ("mean", "sdev", "max", "min", "pkpk"))
        self.write(f"calculate3:format {calc3_fm}")

    def get_calc3_data(self):
        """ Get the calculated data by calculate 3. """
        return self.query("calculate3:data?")
		

    # Complex functions
    def meas_curr_buf(self, volt: float, num, speed) -> Tuple[List, float]:
        """ measure average current? """
        self.set_laser_volt(volt=volt)
        self.set_detect_npl_cycles(speed=speed)
        self.set_trace_source(source="sense")
        self.set_trace_points(pts=num)
        self.set_trace_ctl(ctl="next")
        self.set_trig_count(count=num)
        self.set_laser_state(1)
        self.initiate()
        
        time.sleep(0.1+1*speed+speed*num*0.06)
        trace_data = self.get_trace_data()
        self.set_calc3_format(calc3_fm="mean")

        calc3_data = self.get_calc3_data()
        self.set_trace_ctl(ctl="never")

        currents = [float(trace_data.split(","[5*(i-1)+1])) for i in range(num)]
        current = calc3_data.split(",")[1]
        
        return currents, current
    