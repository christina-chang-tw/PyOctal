import time
from os.path import join

import pandas as pd

from pyoctal.instruments import (
    Keithley6487, 
    AmetekDSP7265,
    AgilentE3640A,
    Keithley2400
)
from pyoctal.instruments.base import BaseSweeps
from pyoctal.utils.file_operations import export_to_csv

class IVSweeps(BaseSweeps):
    """
    IV Sweeps or Current-Voltage Sweeps

    This sweeps through the voltage range and only obtains information about
    the current

    Parameters
    ----------
    ttype_configs: dict
        Test type specific configuration parameters
    addrs: map
        All instrument addresses
    rm:
        Pyvisa resource manager
    folder: str
        Path to the folder
    fname: str
        Filename
    """

    def __init__(self, ttype_configs: dict, addrs: dict, rm, folder: str, fname: str):
        super().__init__(addrs=addrs, rm=rm, folder=folder, fname=fname)
        self.v_start = ttype_configs.v_start
        self.v_stop = ttype_configs.v_stop
        self.v_step = ttype_configs.v_step
        self.t_step = ttype_configs.t_step
        self.currs = []
        self.volts = []
        self.df = pd.DataFrame()


    def run_6487(self):
        self.instrment_check("vs", self._addrs.keys())
        vs = Keithley6487(addr=self._addrs.vs, rm=self._rm)

        vs.set_laser_volt(0)
        vs.set_laser_state(1) # turn the laser on
    
        for volt in range(self.v_start, self.v_stop+self.v_step, self.v_step):
            vs.set_laser_volt(volt)
            time.sleep(self.t_step)

            self.volts.append(volt)
            self.currs.append(vs.meas_curr()) # measure current and append

        self.df["Voltage [V]"] = self.volts
        self.df["Current [A]"] = self.currs
        
        export_to_csv(data=self.df, filename=join(self.folder, f"{self.fname}.csv"))

        vs.set_laser_volt(0) 
        vs.set_laser_state(0) # turn laser off



    def run_DSP7265(self):
        self.instrment_check(("pm", "amp"), self._addrs.keys())
        pm = AgilentE3640A(addr=self._addrs.pm, rm=self._rm)
        amp = AmetekDSP7265(addr=self._addrs.amp, rm=self._rm)
        pm.set_volt(0)
        pm.set_output_state(1)

        optics = []

        for volt in range(self.v_start, self.v_stop+self.v_step, self.v_step):
            pm.set_volt(volt)
            time.sleep(self.t_step)

            self.volts.append(volt)
            self.currs.append(pm.get_curr())
            optics.append(amp.get_mag())

        self.df["Voltage [V]"] = self.volts
        self.df["Current [A]"] = self.currs
        self.df["Amplifier [dB]"] = optics
        
        export_to_csv(data=self.df, filename=join(self.folder, f"{self.fname}.csv"))

        pm.set_volt(0) 
        pm.set_output_state(0) # turn laser off
        amp.set_mag(0)


    def run_dual_DSP7265(self):
        self.instrment_check(("amp", "pm"), self._addrs.keys())
        amp = AmetekDSP7265(addr=self._addrs.amp, rm=self._rm)
        pm1 = AgilentE3640A(addr=self._addrs.pm[0], rm=self._rm)
        pm2 = AgilentE3640A(addr=self._addrs.pm[1], rm=self._rm)

        df = pd.DataFrame(columns=["Volt1 [V]", "Volt2 [V]", "Current1 [A]", "Current2 [A]", "Optical [dB]"])

        # does the voltage range needs to be different for different voltage source???
        for volt1 in range(self.v_start, self.v_stop+self.v_step, self.v_step):
            pm1.set_volt(volt1)
            curr1 = pm1.get_curr()
            for volt2 in range(self.v_start, self.v_stop+self.v_step, self.v_step):
                pm2.set_volt(volt2)
                time.sleep(self.t_step)
                curr2 = pm2.get_curr()
                optical = amp.get_mag()
                data = (volt1, volt2, curr1, curr2, optical)
                df.loc[len(df)] = data
        
        export_to_csv(data=self.df, filename=join(self.folder, f"{self.fname}.csv"))
        pm1.set_volt(0)
        pm1.set_output_state(0) # turn laser off
        pm2.set_volt(0)
        pm2.set_output_state(0) # turn laser off


    def run_E3640A(self):
        self.instrment_check("pm", self._addrs.keys())
        pm = AgilentE3640A(addr=self._addrs.pm, rm=self._rm)
        pm.set_volt(0)
        pm.set_output_state(1)

        for volt in range(self.v_start, self.v_stop+self.v_step, self.v_step):
            pm.set_volt(volt)
            time.sleep(self.t_step)

            self.volts.append(volt)
            self.currs.append(pm.get_curr())

        self.df["Voltage [V]"] = self.volts
        self.df["Current [A]"] = self.currs
        
        export_to_csv(data=self.df, filename=join(self.folder, f"{self.fname}.csv"))

        pm.set_volt(0) 
        pm.set_output_state(0) # turn laser off


    def run_2400(self):
        self.instrment_check("vs", self._addrs.keys())
        smu = Keithley2400(addr=self._addrs.smu, rm=self._rm)
        smu.set_laser_volt(0)
        smu.set_laser_state(1) # turn the laser on

        currents = pd.DataFrame()

        for volt in range(self.v_start, self.v_stop+self.v_step, self.v_step):
            smu.set_laser_volt(volt)
            time.sleep(self.t_step)

            
            currents[f"{volt}V"], curr = smu.meas_curr_buf(volt, 200, 1)
            self.volts.append(curr)
            self.currs.append(curr)
            
        self.df["Voltage [V]"] = self.volts
        self.df["Current [A]"] = self.currs

        # export V-Is
        export_to_csv(data=currents, filename=join(self.folder, f"{self.fname}_VIs.csv"))
        # export V-I
        export_to_csv(data=self.df, filename=join(self.folder, f"{self.fname}.csv"))

        smu.set_laser_volt(0) 
        smu.set_laser_state(0) # turn laser off


