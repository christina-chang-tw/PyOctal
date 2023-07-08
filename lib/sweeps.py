from lib.instruments.pal import PAL
from lib.csv_operations import df_initiate, export_csv
from lib.util import get_func_name


class SWEEPS:
    def __init__(self, dev: PAL):
        self.dev = dev
        dev.activate()

    def iloss(self, args):
        df = df_initiate(args.chip_name, get_func_name())

        self.dev.sweep_params(
            start=args.w1,
            stop=args.w2,
            rate=args.rate,
            power=args.power,
        )
        self.dev.start_meas()
        df[args.cname] = self.dev.get_result()

        export_csv(df, args.chip_name, f'{get_func_name()}_data')



if __name__ == "__main__":
    test = SWEEPS()
    test.iloss()
        
