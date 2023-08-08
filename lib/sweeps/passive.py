from lib.instruments import KeysightILME, Agilent8163B
from lib.util.file_operations import export_to_csv
from lib.util.util import get_func_name, wait_for_next_meas, get_result_dirpath
from lib.base import BaseSweeps
from lib.error import *

from typing import Union
import pandas as pd
from tqdm import tqdm 
import logging



logger = logging.getLogger(__name__)

class ILossSweep(BaseSweeps):
    """
    Insertion Loss Sweeps

    Parameters
    ----------
    instr_addrs:
        A dictionary of the addresses of all instruments used in this sweep
    """
    def __init__(self, instr_addrs: Union[str, list, tuple, dict]):
        super().__init__(instr_addrs=instr_addrs)


    def run_sweep_ilme(self, chip_name: str, configs):
        """ This uses ILME machine to obtain results about insertion loss and  wavelength """
        self.instrment_check("mm", self._addrs.keys())
        mm = Agilent8163B(addr=self._addrs["mm"])
        dev = KeysightILME()
        dev.activate()
        

        df = pd.DataFrame()
        lf = pd.DataFrame()
        
        dev.sweep_params(
                start=configs["w_start"],
                stop=configs["w_stop"],
                step=configs["step"],
                power=configs["power"],
            )

        for i, length in tqdm(enumerate(configs["lengths"]), total=len(configs["lengths"]), desc="ILOSS Sweeps"):
            mm.setup()
            wait_for_next_meas(i, len(configs["lengths"])) # this takes an input to continue to next measurement
            dev.start_meas()
            lf[i], temp = dev.get_result(length)
            df = pd.concat([df, temp], axis=1)
            export_to_csv(df, get_result_dirpath(chip_name), f'{configs["structure"]}_{get_func_name()}_data')

        
        if not lf.eq(lf.iloc[:,0], axis=0).all(axis=1).all(axis=0):
            logger.warning("Discrepancy in wavelengths")


    
        
