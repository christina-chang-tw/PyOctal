from typing import Union
import time
import sys

from pyoctal.base import BaseInstrument


class FiberlabsAMP(BaseInstrument):
    """
    Fiberlabs Desktop Optical Fiber Amplifier

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """
    def __init__(self, addr: str, rm: str):
        super().__init__(rsc_addr=addr, rm=rm)
        


    def set_output_state(self, state: bool):
        """ Set output state. """
        self.write(f"active,{state}")

    def set_ld_mode(self, chan: int, mode: int):
        """ 
        Set the setting of pumpLD driving mode. 
        0 - ALC, 1 - ACC
        """
        self.write(f"setmod:,{chan},{mode}")

    def set_curr(self, chan: int, curr: float):
        """ Set the current for ACC [mA]. """
        self.write(f"setacc,{chan},{curr}")

    def set_output_power(self, chan: int, power: float):
        """ Set the temporary setting of optical output level for ALC [dBm]. """
        self.write(f"setalc,{chan},{power}")



    def get_mon_output_power(self) -> list:
        """ Get output power level [dBm]. """
        out_power = self.query("monout")
        out_power = out_power.split(',').rstrip().lstrip()
        return map(float, out_power)
    
    def get_mon_input_power(self) -> list:
        """ Get input power level [dBm]. """
        in_power = self.query("monin")
        in_power = in_power.split(',').rstrip().lstrip()
        return map(float, in_power)
    
    def get_mon_ret_power(self) -> list:
        """ Get return power level [dBm]. """
        ret_power = self.query("monin")
        ret_power = ret_power.split(',').rstrip().lstrip()
        return map(float, ret_power)
    
    def get_mon_pump_ld(self, chan: int="") -> Union[list, float]:
        """ Get monitor of pumpLD forward current (mA). """
        if chan == "":
            # all channels' forward current
            currs = self.query(f"monldc")
            currs = currs.split(',').rstrip().lstrip()
            return map(float, currs)
        return self.query_float(f"monldc,{chan}")
    
    def get_mon_pump_temp(self, chan: int="") -> Union[list, float]:
        """ Get monitor of pumpLD temperature (deg.C). """
        if chan == "":
            # all channels' forward current
            temps = self.query(f"monldt")
            temps = temps.split(',').rstrip().lstrip()
            return map(float, temps)
        return self.query_float(f"monldt,{chan}")
    
    def get_ld_mode(self, chan: int) -> int:
        """ 
        Get the setting of pumpLD driving mode. 
        0 - ALC, 1 - ACC
        """
        return self.query_int(f"setmod,{chan}")
    
    def get_curr(self, chan: int) -> float:
        """ Get the current for ACC [mA]. """
        return self.query_float(f"setacc,{chan}")

    def get_output_power(self, chan: int) -> float:
        """ Get the optical output power for ALC [dBm]."""
        return self.query_float(f"setalc,{chan}")
    


    def curr_wait_till_stabalise(self, chan: int):
        """ Make sure that the amplifier output current stablise. """
        scale_factor = 0.1 # 10% difference
        diff = sys.maxsize # assign a big value

        prev = self.get_mon_pump_ld(chan)
        while diff > scale_factor*prev:
            new = self.get_mon_pump_ld(chan)
            diff = new - prev
            prev = new
            time.sleep(0.1)
