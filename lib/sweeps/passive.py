from lib.instruments.pal import PAL
from lib.csv_operations import initiate
import inspect

class PASSIVE_TESTING:
    def __init__(self, dev: PAL):
        self.dev = dev
        dev.activate()

    def iloss(self, args):
        initiate(args.chip_name, inspect.getouterframes(inspect.currentframe())[1].function)

        self.dev.sweep_params(
            start=args.w1,
            stop=args.w2,
            rate=args.rate,
            power=args.power,
        )
        df = self.dev.get_result(args.cname)

        
