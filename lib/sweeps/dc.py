from lib.instruments import AgilentE3640A, Agilent8163B, KeysightILME
from lib.base import BaseSweeps
from lib.util.file_operations import export_to_csv
from lib.util.util import get_result_dirpath
from lib.error import *

from typing import Union
import pandas as pd
from tqdm import tqdm 
import logging
import time

logger = logging.getLogger(__name__)


class DCSweeps(BaseSweeps):
    """
    DC Sweeps

    This sweeps through the voltage range and obtains the information
    about the insertion loss against wavelength 

    Parameters
    ----------
    instr_addrs:
        A dictionary of the addresses of all instruments used in this sweep
    """
    def __init__(self, instr_addrs: Union[str, list, tuple, dict]):
        # check if the required device type exist
        super().__init__(instr_addrs=instr_addrs)


    def run_ilme(self, configs):
        """ Run with ILME engine """
        self.instrment_check("pm", self._addrs.keys())

        pm = AgilentE3640A(addr=self._addrs["pm"])
        ilme = KeysightILME()
        ilme.activate()
        df = pd.DataFrame()

        v_start = configs["v_start"]
        v_stop = configs["v_stop"]
        v_step = configs["v_step"]

        for volt in tqdm(range(v_start, v_stop+v_step, v_step)):
            pm.set_volt(volt)
            print(f"Output voltage = {volt}")

            ilme.start_meas()
            temp = ilme.get_result(name=volt)
            df = pd.concat([df, temp], axis=1)
            export_to_csv(df, get_result_dirpath(configs["folder"]), configs["fname"])

        pm.set_volt(0)


    def run_one_source(self, configs):
        """ Run only with instrument. Require one voltage source """
        self.instrment_check(("pm", "mm"), self._addrs.keys())
        pm = AgilentE3640A(addr=self._addrs["pm"])
        mm = Agilent8163B(addr=self._addrs["mm"])

        v_start = configs["v_start"]
        v_stop = configs["v_stop"]
        v_step = configs["v_step"]
        currents = []
        df = pd.DataFrame()

        for volt in tqdm(range(v_start, v_stop+v_step, v_step)):
            pm.set_volt(volt)
            time.sleep(0.1)
            currents = currents.append(pm.get_curr()) # get the current value

            pm.set_volt(0)

            # get the sweep value
            df[f"{volt}V"] = mm.run_laser_sweep_auto(
                power=configs["power"], 
                lambda_start=configs["lambda_start"],
                lambda_stop=configs["lambda_stop"],
                lambda_step=configs["lambda_step"]*pow(10, 3),
                lambda_speed=configs["lambda_speed"]
                )
            
            export_to_csv(df, get_result_dirpath(configs["folder"]), configs["fname"])
            export_to_csv(pd.Series(currents), get_result_dirpath(configs["folder"]), "dc_currents")
        
        pm.set_volt(0)
        pm.set_output_state(0)
        

    def run_dual_sources(self, configs):
        """ Run only with instrument. Require two voltage sources """
        v_start = configs["v_start"]
        v_stop = configs["v_stop"]
        v_step = configs["v_step"]



        
        

        
