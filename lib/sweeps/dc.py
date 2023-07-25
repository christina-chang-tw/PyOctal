from lib.instruments import KeysightILME, AgilentE3640A, AgilentE3645
from lib.base import BaseSweeps
from lib.util.file_operations import export_to_csv

from typing import Union
import pandas as pd
from tqdm import tqdm 
import logging

logger = logging.getLogger(__name__)

class DCSweeps(BaseSweeps):
    def __init__(self, instr: Union[AgilentE3645, AgilentE3640A]):
        self.dev = KeysightILME()
        self.dev.activate()
        super().__init__(instr=instr)

    def run_sweep(self, chip_name, configs):
        df = pd.DataFrame()
        lf = pd.DataFrame()

        v_start = configs["v_start"]
        v_stop = configs["v_stop"]
        v_step = configs["v_step"]

        for i, volt in tqdm(enumerate(range(v_start, v_stop+v_step, v_step))):
            self.instr.set_volt(volt=volt)
            print(f"Output voltage = {volt}")

            self.dev.start_meas()
            lf[i], temp = self.dev.get_result(volt)
            df = pd.concat([df, temp], axis=1)
            export_to_csv(df, chip_name, f'{configs["structure"]}_{self.__get_name()}_data')

        self.instr.set_volt(volt=0)



        
        

        
