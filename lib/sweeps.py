from lib.instruments.pas import ILME
from lib.csv_operations import create_folder, export_csv
from lib.util import get_func_name, wait_for_next_meas

import lib.analysis as analysis
import numpy as np
import pandas as pd


class Sweeps:
    def __init__(self, dev: ILME):
        self.dev = dev
        dev.activate()

    def iloss(self, chip_name, args):
        df = pd.DataFrame()
        lf = pd.DataFrame()
        
        self.dev.sweep_params(
                start=args.range[0],
                stop=args.range[1],
                step=args.step[0],
                power=args.power[0],
            )

        for i, length in enumerate(args.lengths):
            self.dev.start_meas()
            lf[i], df[float(length)] = self.dev.get_result()
            wait_for_next_meas()
        
        x = lf.eq(lf.iloc[:, 0], axis=0).all(axis=1)
        
        # analysis.iloss(df, np.array(lf.iloc[:,1]), chip_name)

        export_csv(lf, chip_name, f'{get_func_name()}_lambda')
        export_csv(df, chip_name, f'{get_func_name()}_data')

        
