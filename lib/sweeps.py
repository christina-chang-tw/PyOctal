from lib.instruments.pas import ILME
from lib.csv_operations import export_csv
from lib.util import get_func_name, wait_for_next_meas
import lib.analysis as analysis
from lib.instruments.multimeter import M_8163B

import pandas as pd
import numpy as np
from tqdm import tqdm 
import logging

logger = logging.getLogger(__name__)

class Sweeps:
    def __init__(self, dev: ILME, instr):
        self.dev = dev
        self.instr = instr
        self.dev.activate()

    def iloss(self, chip_name, args):
        df = pd.DataFrame()
        lf = pd.DataFrame()
        
        self.dev.sweep_params(
                start=args.range[0],
                stop=args.range[1],
                step=args.step[0],
                power=args.power[0],
            )


        for i, length in tqdm(enumerate(args.lengths), total=len(args.lengths), desc="ILOSS Sweeps"):
            self.instr.setup()
            wait_for_next_meas(i, len(args.lengths)) # this takes an input to continue to next measurement
            self.dev.start_meas()
            lf[i], temp = self.dev.get_result(length)
            df = pd.concat([df, temp], axis=1)
            export_csv(df, chip_name, f'{get_func_name()}_data')

        
        if not lf.eq(lf.iloc[:, 0], axis=0).all(axis=1).all(axis=0):
            logger.warning("Discrepancy in wavelengths")
        
        df_coeff = analysis.iloss(df, np.array(lf.iloc[:,1]), self.dev.get_no_channels(), chip_name)
        export_csv(df_coeff, chip_name, f'{get_func_name()}_coeffs')

        
