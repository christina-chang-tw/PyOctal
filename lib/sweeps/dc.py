from lib.instruments import AgilentE3640A, AgilentE3645
from lib.base import BaseSweeps
from lib.util.file_operations import export_to_csv
from lib.util.util import get_result_dirpath

from typing import Union
import pandas as pd
from tqdm import tqdm 
import logging
import time

logger = logging.getLogger(__name__)

class DCSweeps(BaseSweeps):
    def __init__(self, instr: Union[AgilentE3645, AgilentE3640A]):
        super().__init__(instr=instr)

    def run_sweep_ilme(self, configs):
        """ Run with ILME engine """
        #dev = KeysightILME()
        dev = 0
        dev.activate()
        df = pd.DataFrame()

        v_start = configs["v_start"]
        v_stop = configs["v_stop"]
        v_step = configs["v_step"]

        for volt in tqdm(range(v_start, v_stop+v_step, v_step)):
            self.instr.set_volt(volt)
            print(f"Output voltage = {volt}")

            dev.start_meas()
            temp = dev.get_result(name=volt)
            df = pd.concat([df, temp], axis=1)
            export_to_csv(df, get_result_dirpath(configs["folder"]), configs["fname"])

        self.instr.set_volt(0)


    def run_sweep_instr(self, configs):
        """ Run only with the instrument """

        v_start = configs["v_start"]
        v_stop = configs["v_stop"]
        v_step = configs["v_step"]
        currents = []
        df = pd.DataFrame()

        for volt in tqdm(range(v_start, v_stop+v_step, v_step)):
            self.instr.set_volt(volt)
            time.sleep(0.1)
            currents = currents.append(self.instr.get_curr()) # get the current value

            self.instr.set_volt(0)

            # get the sweep value
            df[f"{volt}V"] = self.instr.run_laser_sweep_auto(
                power=configs["power"], 
                lambda_start=configs["lambda_start"],
                lambda_stop=configs["lambda_stop"],
                lambda_step=configs["lambda_step"]*pow(10, 3),
                lambda_speed=configs["lambda_speed"]
                )
            
            export_to_csv(df, get_result_dirpath(configs["folder"]), configs["fname"])
            export_to_csv(pd.Series(currents), get_result_dirpath(configs["folder"]), "dc_currents")
        
        self.instr.set_volt(0)
        self.instr.set_laser_state(0)
        


        
        

        
