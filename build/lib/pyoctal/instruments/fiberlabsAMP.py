from typing import Union, List
import time
import sys

from pyvisa import ResourceManager

from pyoctal.instruments.base import BaseInstrument
from pyoctal.utils.error import PARAM_INVALID_ERR, error_message
from pyoctal.utils.util import watt_to_dbm, dbm_to_watt


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
    def __init__(self, rm: ResourceManager):
        super().__init__(rm=rm, read_termination="")
        self._chan_curr_max = 1048 # [mA]
        self._chan_power_max = 398.11 # [mW]
    
    @property
    def chan_curr_max(self):
        return self._chan_curr_max
    
    @property
    def chan_power_max(self):
        return self._chan_power_max

    def write(self, cmd):
        """ To bypass the return string when setting values. """
        _ = self.query(cmd)

    def query_monitor(self, cmd: str, all_chan: bool):
        """ 
        Return float numbers that are querying about monitor.

        Returned values from the instrument are in the format of a 
        string list.
        i.e. "1.0,2.0,N/A,N/A"
         
        Parameters:
        -----------
        all_chan: bool
            If true, it is a query to get valuesfor all_chan channels.
        """
        rsp = self.query(cmd)
        if not all_chan:
            return float(rsp)
        rsp = rsp.rstrip().split(',')
        rsp = [float(val if val != "N/A" else "-100") for val in rsp]
        return rsp
    

    def query_setting(self, cmd: str, all_chan: bool):
        """ 
        Return float numbers that are querying about settings.

        Returned values from the instrument are in the format of a 
        string list.
        i.e. "SETMOD,1,1"
         
        Parameters:
        -----------
        all_chan: bool
            If true, it is a query to get valuesfor all_chan channels.
        """
        rsp = self.query(cmd)
        rsp = rsp.rstrip().split(',')
        if not all_chan:
            return float(rsp[-1])
        rsp = list(map(float, rsp[1:]))
        return rsp


    def set_output_state(self, state: bool):
        """ Set output state. """
        self.write(f"active,{state}")

    def set_ld_mode(self, chan: int, mode: Union[int, str]):
        """ 
        Set the setting of pumpLD driving mode. 
        0 - ALC, 1 - ACC
        """

        if isinstance(mode, str):
            mode = 0 if mode == "ALC" else 1
        if chan != 1 and mode == 0:
            raise ValueError(f"Error code {PARAM_INVALID_ERR:x}: {error_message[PARAM_INVALID_ERR]}. Only Channel 1 can be set to ALC")
        self.write(f"setmod:,{chan},{mode}")

    def set_curr_smart(self, mode: str, val: float):
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

        boundary = val//chan_max + 1
        val = val%chan_max

        for chan in range(1, 5):
            if chan < boundary:
                 # set channels below the boundary to maximum
                func(chan, chan_max)
            elif chan == boundary:
                # set channel at the boundary to the correct current
                func(chan, val)
            else:
                # set channels above the boundary to 0mA
                func(chan, 0)
        
            # make sure the last set channel is stabalised
            self.wait_till_curr_is_stabalised(chan=chan)

    def set_all_curr(self, curr: float):
        for chan in range(1, 5):
            self.set_curr(chan=chan, curr=curr)

    def set_curr(self, chan: int, curr: float):
        """ Set the temporary setting of the current for ACC [mW]. """
        self.write(f"setacc,{chan},{curr}")

    def set_power(self, chan: int, power: float):
        """ Set the temporary setting of optical output level for ALC [mW]. """
        power = watt_to_dbm(power)
        self.write(f"setalc,{chan},{power}")


    def get_mon_output_power(self) -> List:
        """ Get output power level [mW]. """
        powers = self.query_monitor("monout", all_chan=True)
        print(powers)
        powers = list(map(dbm_to_watt, powers))
        print(powers)
        return powers
    
    def get_mon_input_power(self) -> List:
        """ Get input power level [mW]. """
        powers = self.query_monitor("monin", all_chan=True)
        powers = list(map(dbm_to_watt, powers))
        return powers
    
    def get_mon_ret_power(self) -> List:
        """ Get return power level [mW]. """
        powers = self.query_monitor("monret", all_chan=True)
        powers = list(map(dbm_to_watt, powers))
        return powers
    
    def get_mon_pump_curr(self, chan: int=None) -> Union[List, float]:
        """ Get monitor of pumpLD forward current (mA). """
        if not chan:
            # all channels' forward current
            return self.query_monitor("monldc,", all_chan=True)
        return self.query_monitor(f"monldc,{chan}", all_chan=False)
        
    def get_mon_pump_temp(self, chan: int=None) -> Union[List, float]:
        """ Get monitor of pumpLD temperature (deg.C). """
        if not chan:
            # all channels' forward current
            return self.query_monitor("monldt,", all_chan=True)
        return self.query_monitor(f"monldt,{chan}", all_chan=False)
    
    def get_ld_mode(self, chan: int=None) -> int:
        """ 
        Get the setting of pumpLD driving mode. 
        0 - ALC, 1 - ACC
        """
        if not chan:
            # all channels' driving mode
            return self.query_setting("setmod,", all_chan=True)
        return self.query_setting(f"setmod,{chan}", all_chan=False)
    
    def get_curr(self, chan: int=None) -> float:
        """ Get the temporary setting of current for ACC [mA]. """
        if not chan:
            # all channels' driving mode
            return self.query_setting("setacc,", all_chan=True)
        return self.query_setting(f"setacc,{chan}", all_chan=False)

    def get_power(self, chan: int=None) -> float:
        """ Get the optical output power for ALC [mW]."""
        if not chan:
            # all channels' driving mode
            powers = self.query_setting("setalc,", all_chan=True)
            powers = list(map(dbm_to_watt, powers))
            return powers
        return dbm_to_watt(self.query_setting(f"setalc,{chan}", all_chan=False))
    


    def wait_till_curr_is_stabalised(self, chan: int):
        """ Make sure that the amplifier output current stablise. """
        scale_factor = 0.1 # 10% difference
        diff = sys.maxsize # assign a big value

        prev = self.get_mon_pump_curr(chan=chan)
        while diff > scale_factor*prev:
            new = self.get_mon_pump_curr(chan=chan)
            diff = new - prev
            prev = new
            time.sleep(0.1)
