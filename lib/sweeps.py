from lib.instruments.pal import PAL
from lib.csv_operations import create_folder, export_csv
from lib.util import get_func_name, wait_for_next_meas
import lib.analysis as analysis

import numpy as np
import pandas as pd


class Sweeps:
    def __init__(self, dev: PAL):
        self.dev = dev
        dev.activate()

    def iloss(self, args):
        create_folder(args.chip_name, get_func_name())
        df = pd.DataFrame()
        lf = pd.DataFrame() 
        
        self.dev.sweep_params(
                start=args.range[0],
                stop=args.range[1],
                rate=args.rate,
                power=args.power,
            )

        for i, length in enumerate(args.lengths):
            self.dev.start_meas()
            df[float(length)], lf[i] = self.dev.get_result()
            wait_for_next_meas()
        
        if lf.eq(lf.iloc[:, 0], axis=0).all(axis=1):
            raise Exception("Wavelength spacing are not equal!")
        
        analysis.loss(df, np.array(lf.iloc[:,1]), args.chip_name)

        export_csv(lf, args.chip_name, f'{get_func_name()}_lambda')
        export_csv(df, args.chip_name, f'{get_func_name()}_data')



if __name__ == "__main__":
    test = Sweeps()
    test.iloss()
        
