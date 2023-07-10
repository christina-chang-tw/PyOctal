from lib.csv_operations import export_csv, package_info
from lib.util import get_func_name

class Test_Info():
    """ Information about tests that are run and export to an info file in csv format """
    @staticmethod
    def iloss(chip_name, args):
        info = {
            "Testing Type" : "Insertion Loss",
            "Power [dBm]" : args.power[0],
            "Start lambda [nm]" : args.w1[0],
            "Stop lambda [nm]" : args.w2[0],
            "Sweep rate [nm/s]" : args.rate[0],
        }
        export_csv(package_info(info), chip_name, f'{get_func_name()}_info')


    