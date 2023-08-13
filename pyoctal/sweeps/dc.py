import pandas as pd
from tqdm import tqdm 
import time

from pyoctal.instruments import AgilentE3640A, Agilent8163B, KeysightILME
from pyoctal.base import BaseSweeps
from pyoctal.util.file_operations import export_to_csv

class DCSweeps(BaseSweeps):
    """
    DC Sweeps

    This sweeps through the voltage range and obtains the information
    about the insertion loss against wavelength 

    Parameters
    ----------
    configs:
        A map containing all parameters. Should be read from a yaml file
    rm:
        Pyvisa resource manager
    """
    def __init__(self, configs: dict, rm):
        # check if the required device type exist
        super().__init__(instr_addrs=configs.instr_addrs, rm=rm, folder=configs.folder, fname=configs.fname)
        self.v_start = configs.v_start
        self.v_stop = configs.v_stop
        self.v_step = configs.v_step
        self.cycles = configs.cycles
        self.w_start=configs.lambda_start,
        self.w_stop=configs.lambda_stop,
        self.w_step=configs.lambda_step*pow(10, 3)
        self.w_speed=configs.lambda_speed
        self.power = configs.power
        self.currents = []
        self.df = pd.DataFrame()


    def run_ilme(self):
        """ Run with ILME engine """
        self.instrment_check("pm", self._addrs.keys())

        pm = AgilentE3640A(addr=self._addrs.pm, rm=self._rm)
        ilme = KeysightILME()
        ilme.activate()

        for volt in tqdm(range(self.v_start, self.v_stop+self.v_step, self.v_step)):
            pm.set_volt(volt)
            time.sleep(0.1)
            self.currents.append(pm.get_curr()) # get the current value

            ilme.start_meas()
            temp = ilme.get_result(name=volt)
            self.df = pd.concat([self.df, temp], axis=1)
            export_to_csv(self.df, self.folder, self.fname)
            export_to_csv(pd.Series(self.currents), self.folder, "dc_currents")

        pm.set_volt(0)


    def run_one_source(self):
        """ Run only with instrument. Require one voltage source """
        self.instrment_check(("pm", "mm"), self._addrs.keys())
        pm = AgilentE3640A(addr=self._addrs.pm, rm=self._rm)
        mm = Agilent8163B(addr=self._addrs.mm, rm=self._rm)

        for volt in tqdm(range(self.v_start, self.v_stop+self.v_step, self.v_step)):
            pm.set_volt(volt)
            time.sleep(0.1)
            self.currents.append(pm.get_curr()) # get the current value

            pm.set_volt(0)

            # get the loss v.s. wavelength
            self.df[f"{volt}V"] = mm.run_laser_sweep_auto(
                power=self.power, 
                lambda_start=self.w_start,
                lambda_stop=self.w_stop,
                lambda_step=self.w_step,
                lambda_speed=self.w_speed,
                cycles=self.cycles,
                )
            
            export_to_csv(self.df, self.folder, self.fname)
            export_to_csv(pd.Series(self.currents), self.folder, "dc_currents")
        
        pm.set_volt(0)
        pm.set_output_state(0)

        
        

        
