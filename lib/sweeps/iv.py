from lib.instruments import (
    Keithley6487, 
    AmetekDSP7265,
    AgilentE3640A,
    Keithley2400
)
from lib.base import BaseSweeps
from lib.util.util import get_result_dirpath
from lib.util.file_operations import export_to_csv

import time
import pandas as pd
from typing import Union

class IVSweeps(BaseSweeps):
    """
    IV Sweeps or Current-Voltage Sweeps

    This sweeps through the voltage range and only obtains information about
    the current

    Parameters
    ----------
    instr_addrs:
        A dictionary of the addresses of all instruments used in this sweep
    """

    def __init__(self, instr_addrs: Union[str, list, tuple, dict]):
        super().__init__(instr_addrs=instr_addrs)
        self.currs = []
        self.volts = []
        self.df = pd.DataFrame()


    def run_6487(self, configs):
        self.instrment_check("vs", self._addrs.keys())
        vs = Keithley6487(addr=self._addrs["vs"])

        v_start = configs["v_start"]
        v_stop = configs["v_stop"]
        v_step = configs["v_step"]
        
        vs.set_laser_volt(0)
        vs.set_laser_state(1) # turn the laser on
    
        for volt in range(v_start, v_stop+v_step, v_step):
            vs.set_laser_volt(volt)
            time.sleep(0.01) # pause the plotting

            self.volts.append(volt)
            self.currs.append(vs.meas_curr()) # measure current and append

        self.df["Voltage (V)"] = self.volts
        self.df["Current (A)"] = self.currs
        
        export_to_csv(data=self.df, path=get_result_dirpath(configs["folders"]), fname=configs["fname"])

        vs.set_laser_volt(0) 
        vs.set_laser_state(0) # turn laser off



    def run_DSP7265(self, configs):
        self.instrment_check(("pm", "amp"), self._addrs.keys())
        pm = AgilentE3640A(addr=self._addrs["pm"])
        amp = AmetekDSP7265(addr=self._addrs["amp"])
        pm.set_volt(0)
        pm.set_output_state(1)

        v_start = configs["v_start"]
        v_stop = configs["v_stop"]
        v_step = configs["v_step"]
        t_step = configs["t_step"]

        optics = []

        for volt in range(v_start, v_stop+v_step, v_step):
            pm.set_volt(volt)
            time.sleep(t_step)

            self.volts.append(volt)
            self.currs.append(pm.get_curr())
            optics.append(amp.get_mag())

        self.df["Voltage (V)"] = self.volts
        self.df["Current (A)"] = self.currs
        self.df["Amplifier (dB)"] = optics
        
        export_to_csv(data=self.df, path=get_result_dirpath(configs["folders"]), fname=configs["fname"])

        pm.set_volt(0) 
        pm.set_output_state(0) # turn laser off
        amp.set_mag(0)



    def run_E3640A(self, configs):
        self.instrment_check("pm", self._addrs.keys())
        pm = AgilentE3640A(addr=self._addrs["pm"])
        pm.set_volt(0)
        pm.set_output_state(1)

        v_start = configs["v_start"]
        v_stop = configs["v_stop"]
        v_step = configs["v_step"]
        t_step = configs["t_step"]


        for volt in range(v_start, v_stop+v_step, v_step):
            pm.set_volt(volt)
            time.sleep(t_step)

            self.volts.append(volt)
            self.currs.append(pm.get_curr())

        self.df["Voltage (V)"] = self.volts
        self.df["Current (A)"] = self.currs
        
        export_to_csv(data=self.df, path=get_result_dirpath(configs["folders"]), fname=configs["fname"])

        pm.set_volt(0) 
        pm.set_output_state(0) # turn laser off


    def run_2400(self, configs):
        self.instrment_check("vs", self._addrs.keys())
        vs = Keithley2400(addr=self._addrs["vs"])
        vs.set_laser_volt(0)
        vs.set_laser_state(1) # turn the laser on

        v_start = configs["v_start"]
        v_stop = configs["v_stop"]
        v_step = configs["v_step"]
        t_step = configs["t_step"]

        currents = pd.DataFrame()

        for volt in range(v_start, v_stop+v_step, v_step):
            vs.set_laser_volt(volt)
            time.sleep(t_step)

            
            currents[f"{volt}V"], curr = vs.meas_curr_buf(volt, 200, 1)
            self.volts.append(curr)
            self.currs.append(curr)
            
        self.df["Voltage (V)"] = self.volts
        self.df["Current (A)"] = self.currs

        # export V-Is
        export_to_csv(data=currents, path=get_result_dirpath(configs["folders"]), fname=f'{configs["fname"]}_VIs')
        # export V-I
        export_to_csv(data=self.df, path=get_result_dirpath(configs["folders"]), fname=configs["fname"])

        vs.set_laser_volt(0) 
        vs.set_laser_state(0) # turn laser off


