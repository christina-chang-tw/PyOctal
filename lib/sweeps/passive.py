from lib.instruments import KeysightILME, Agilent8163B
from lib.util.file_operations import export_to_csv
from lib.util.util import get_func_name, wait_for_next_meas, get_result_dirpath
from lib.base import BaseSweeps

import sys
import pandas as pd
from tqdm import tqdm 
import logging
import time


logger = logging.getLogger(__name__)

class PASILossSweep(BaseSweeps):
    """
    Photonic Application Suite ILME Sweeps.
    This uses ILME machine to obtain results about insertion loss and  wavelength

    Parameters
    ----------
    instr: 
        An instrument used in this sweep
    """
    def __init__(self, instr: Agilent8163B):
        self.dev = KeysightILME()
        self.dev.activate()
        super().__init__(instr=instr)

    def run_sweep(self, chip_name: str, configs):
        df = pd.DataFrame()
        lf = pd.DataFrame()
        
        self.dev.sweep_params(
                start=configs["w_start"],
                stop=configs["w_stop"],
                step=configs["step"],
                power=configs["power"],
            )

        for i, length in tqdm(enumerate(configs["lengths"]), total=len(configs["lengths"]), desc="ILOSS Sweeps"):
            self.instr.setup()
            wait_for_next_meas(i, len(configs["lengths"])) # this takes an input to continue to next measurement
            self.dev.start_meas()
            lf[i], temp = self.dev.get_result(length)
            df = pd.concat([df, temp], axis=1)
            export_to_csv(df, get_result_dirpath(chip_name), f'{configs["structure"]}_{get_func_name()}_data')

        
        if not lf.eq(lf.iloc[:,0], axis=0).all(axis=1).all(axis=0):
            logger.warning("Discrepancy in wavelengths")
        

class InstrILossSweep(BaseSweeps):
    """
    Instrument Insertion Loss Sweep.
    This directly interfaces with instruments to obtain insertion loss data

    Parameters
    ----------
    instr: 
        An instrument used in this sweep
    """
    def __init__(self, instr: Agilent8163B):
        super().__init__(instr=instr)

    


    
        
