import time
import pandas as pd

from lib.instruments import (
    Keithley6487, 
    AmetekDSP7265,
    AgilentE3640A,
    Keithley2400
)
from lib.base import BaseSweeps
from lib.util.util import get_result_dirpath
from lib.util.file_operations import export_to_csv

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

    def __init__(self, configs: dict):
        super().__init__(instr_addrs=configs.instr_addrs, folder=configs.folder, fname=configs.fname)
        
        self.v_start = configs.v_start
        self.v_stop = configs.v_stop
        self.v_step = configs.v_step
        self.t_step = configs.t_step
        self.currs = []
        self.volts = []
        self.df = pd.DataFrame()


    def run_6487(self):
        self.instrment_check("vs", self._addrs.keys())
        vs = Keithley6487(addr=self._addrs.vs)

        vs.set_laser_volt(0)
        vs.set_laser_state(1) # turn the laser on
    
        for volt in range(self.v_start, self.v_stop+self.v_step, self.v_step):
            vs.set_laser_volt(volt)
            time.sleep(self.t_step)

            self.volts.append(volt)
            self.currs.append(vs.meas_curr()) # measure current and append

        self.df["Voltage [V]"] = self.volts
        self.df["Current [A]"] = self.currs
        
        export_to_csv(data=self.df, path=get_result_dirpath(self.folder), fname=self.fname)

        vs.set_laser_volt(0) 
        vs.set_laser_state(0) # turn laser off



    def run_DSP7265(self):
        self.instrment_check(("pm", "amp"), self._addrs.keys())
        pm = AgilentE3640A(addr=self._addrs.pm)
        amp = AmetekDSP7265(addr=self._addrs.amp)
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
        
        export_to_csv(data=self.df, path=get_result_dirpath(self.folder), fname=self.fname)

        pm.set_volt(0) 
        pm.set_output_state(0) # turn laser off
        amp.set_mag(0)


    def run_dual_DSP7265(self):
        self.instrment_check(("amp", "pm"), self._addrs.keys())
        amp = AmetekDSP7265(addr=self._addrs.amp)
        pm1 = AgilentE3640A(addr=self._addrs.pm[0])
        pm2 = AgilentE3640A(addr=self._addrs.pm[1])

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
        
        export_to_csv(data=self.df, path=get_result_dirpath(self.folder), fname=self.fname)
        pm1.set_volt(0)
        pm1.set_output_state(0) # turn laser off
        pm2.set_volt(0)
        pm2.set_output_state(0) # turn laser off


    def run_E3640A(self):
        self.instrment_check("pm", self._addrs.keys())
        pm = AgilentE3640A(addr=self._addrs.pm)
        pm.set_volt(0)
        pm.set_output_state(1)

        for volt in range(self.v_start, self.v_stop+self.v_step, self.v_step):
            pm.set_volt(volt)
            time.sleep(self.t_step)

            self.volts.append(volt)
            self.currs.append(pm.get_curr())

        self.df["Voltage [V]"] = self.volts
        self.df["Current [A]"] = self.currs
        
        export_to_csv(data=self.df, path=get_result_dirpath(self.folder), fname=self.fname)

        pm.set_volt(0) 
        pm.set_output_state(0) # turn laser off


    def run_2400(self):
        self.instrment_check("vs", self._addrs.keys())
        smu = Keithley2400(addr=self._addrs.smu)
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
        export_to_csv(data=currents, path=get_result_dirpath(self.folder), fname=f'{self.fname}_VIs')
        # export V-I
        export_to_csv(data=self.df, path=get_result_dirpath(self.folder), fname=self.fname)

        smu.set_laser_volt(0) 
        smu.set_laser_state(0) # turn laser off


