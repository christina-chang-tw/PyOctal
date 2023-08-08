from lib.instruments import KeysightILME, Agilent8163B
from lib.util.file_operations import export_to_csv
from lib.util.util import wait_for_next_meas, get_result_dirpath
from lib.base import BaseSweeps


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
    def __init__(self, configs: dict):
        super().__init__(instr_addrs=configs["instr_addr"], folder=configs["folder"], fname=configs["fname"])
        self.w_start = configs["w_start"]
        self.w_stop = configs["w_stop"]
        self.w_step = configs["step"]
        self.power = configs["power"]


    def run_sweep_ilme(self, lengths):
        """ This uses ILME machine to obtain results about insertion loss and  wavelength """
        self.instrment_check("mm", self._addrs.keys())
        mm = Agilent8163B(addr=self._addrs["mm"])
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
            export_to_csv(df, get_result_dirpath(self.folder), f'{self.fname}')

        
        if not lf.eq(lf.iloc[:,0], axis=0).all(axis=1).all(axis=0):
            logger.warning("Discrepancy in wavelengths")


    
        
