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
        super().__init__(rsc_addr=addr, rm=rm, read_termination="")
        self.chan_curr_max = 1048
        self.chan_power_max = 10
        
    def write(self, cmd):
        """ To bypass the return string when setting values. """
        _ = self.query(cmd)

    def query_float(self, cmd: str, all: bool):
        """ 
        Return float numbers.
         
        Parameters:
        -----------
        all: bool
            If true, it is a query to get valuesfor all channels.
        """
        rsp = self.query(cmd)
        rsp = rsp.rstrip().split(',')
        if all:
            rsp = list(map(float, rsp[1:]))
        else:
            rsp = float(rsp[-1])
        return rsp

    def set_output_state(self, state: bool):
        """ Set output state. """
        self.write(f"active,{state}")

    def set_ld_mode(self, chan: int, mode: int):
        """ 
        Set the setting of pumpLD driving mode. 
        0 - ALC, 1 - ACC
        """
        self.write(f"setmod:,{chan},{mode}")

    def set_vals_smart(self, mode: str, val: float):
        """ 
        Smarter way of setting current or power.

        Figure out what each channel current setting should be
        from the current that you want to set.
        """
        if mode == "ACC":
            func = self.set_curr
            chan_max = self.chan_curr_max
        elif mode == "ALC":
            func = self.set_power
            chan_max = self.chan_power_max

        boundary = val/chan_max + 1
        val = val%chan_max

        # set channels below the boundary to maximum
        for chan in range(1, boundary):
            func(chan, chan_max)
        # set channels above the boundary to 0mA
        for chan in range(boundary+1, 5):
            func(chan, 0)
        # set channel at the boundary to the correct current
        func(boundary, val)


    def set_curr(self, chan: int, curr: float):
        """ Set the temporary setting of the current for ACC [mA]. """
        self.write(f"setacc,{chan},{curr}")

    def set_power(self, chan: int, power: float):
        """ Set the temporary setting of optical output level for ALC [dBm]. """
        self.write(f"setalc,{chan},{power}")



    def get_mon_output_power(self) -> list:
        """ Get output power level [dBm]. """
        return self.query_float("monout", all=True)
    
    def get_mon_input_power(self) -> list:
        """ Get input power level [dBm]. """
        return self.query_float("monin", all=True)
    
    def get_mon_ret_power(self) -> list:
        """ Get return power level [dBm]. """
        return self.query_float("monret", all=True)
    
    def get_mon_pump_curr(self, chan: int="") -> Union[list, float]:
        """ Get monitor of pumpLD forward current (mA). """
        if chan == "":
            # all channels' forward current
            return self.query_float("monldc", all=True)
        return self.query_float(f"monldc,{chan}", all=False)
        
    def get_mon_pump_temp(self, chan: int="") -> Union[list, float]:
        """ Get monitor of pumpLD temperature (deg.C). """
        if chan == "":
            # all channels' forward current
            return self.query_float("monldt", all=True)
        return self.query_float(f"monldt,{chan}", all=False)
    
    def get_ld_mode(self, chan: int) -> int:
        """ 
        Get the setting of pumpLD driving mode. 
        0 - ALC, 1 - ACC
        """
        return self.query_float(f"setmod,{chan}", all=False)
    
    def get_curr(self, chan: int) -> float:
        """ Get the temporary setting of current for ACC [mA]. """
        return self.query_float(f"setacc,{chan}", all=False)

    def get_power(self, chan: int) -> float:
        """ Get the optical output power for ALC [dBm]."""
        return self.query_float(f"setalc,{chan}", all=False)
    


    def wait_till_curr_is_stabalised(self, chan: int):
        """ Make sure that the amplifier output current stablise. """
        scale_factor = 0.1 # 10% difference
        diff = sys.maxsize # assign a big value

        prev = self.get_mon_pump_ld(chan=chan)
        while diff > scale_factor*prev:
            new = self.get_mon_pump_ld(chan=chan)
            diff = new - prev
            prev = new
            time.sleep(0.1)
