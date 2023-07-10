from lib.csv_operations import export_csv, package_info
from lib.util import get_func_name

class Test_Info():

    @staticmethod
    def iloss(chip_name, args):
        info = {
            "Testing Type" : "Insertion Loss",
            "Power" : args.power[0],
            "Start lambda" : args.w1[0],
            "Stop lambda" : args.w2[0],
            "Sweep rate" : args.rate[0]
        }
        export_csv(package_info(info), chip_name, f'{get_func_name()}_info')


    