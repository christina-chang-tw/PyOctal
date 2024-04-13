from os.path import join

import pandas as pd
from tqdm import tqdm

from pyoctal.instruments import KeysightILME, Agilent8163B
from pyoctal.utils.file_operations import export_to_csv
from pyoctal.instruments.base import BaseSweeps

import logging

logger = logging.getLogger(__name__)

def wait_for_next_meas(i, total):
    print("\r")
    input(f"{i}/{total} : Press ENTER to continue")

class ILossSweep(BaseSweeps):
    """
    Insertion Loss Sweeps

    Parameters
    ----------
    ttype_configs: dict
        Test type specific configuration parameters
    instr_addrs: map
        All instrument addresses
    rm:
        Pyvisa resource manager
    folder: str
        Path to the folder
    fname: str
        Filename
    """
    def __init__(self, ttype_configs: dict, instr_addrs: dict, rm, folder: str, fname: str):
        super().__init__(instr_addrs=instr_addrs, rm=rm, folder=folder, fname=fname)
        self.w_start = ttype_configs.w_start
        self.w_stop = ttype_configs.w_stop
        self.w_step = ttype_configs.w_step
        self.power = ttype_configs.power


    def run_ilme(self, lengths):
        """ This uses ILME machine to obtain results about insertion loss and  wavelength """
        self.instrment_check("mm", self._addrs.keys())
        mm = Agilent8163B(addr=self._addrs.mm, rm=self._rm)
        dev = KeysightILME()
        dev.activate()
        

        df = pd.DataFrame()
        lf = pd.DataFrame()
        
        dev.sweep_params(
                start=self.w_start,
                stop=self.w_stop,
                step=self.w_step,
                power=self.power,
            )

        for i, length in tqdm(enumerate(lengths), total=len(lengths), desc="ILOSS Sweeps"):
            mm.setup()
            wait_for_next_meas(i, len(lengths)) # this takes an input to continue to next measurement
            dev.start_meas()
            lf[i], temp = dev.get_result(length)
            df = pd.concat([df, temp], axis=1)
            export_to_csv(data=self.df, filename=join(self.folder, f"{self.fname}.csv"))

        
        if not lf.eq(lf.iloc[:,0], axis=0).all(axis=1).all(axis=0):
            logger.warning("Discrepancy in wavelengths")


    
        
