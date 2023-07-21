from lib.sweeps.info import TestInfo
from lib.sweeps.passive import PASILossSweep
from lib.sweeps.dc import DCSweeps
from lib.instruments.agilent8163B import Agilent8163B
from lib.instruments.agilentE364X import AgilentE3640A
from lib.util.file_operations import create_folder
from lib.util.logger import CustomFormatter
from lib.util.util import version_check, get_gpib_full_addr, get_config_dirpath

import argparse
from datetime import datetime
import logging
import yaml

TEST_TYPES = ("passive", "dc", "ac")


class PrintSubparserInfo():
    """ Print subparser-dependent information to the CMD output """

    def __init__(self, configs):
        self.configs = configs

    def iloss(self):
        print(f'{"Length [um]":<25} : {", ".join([str(round(i, 2)) for i in self.configs["lengths"]])}')
        print(f'{"Output power [dBm]":<25} : {self.configs["power"]:<6}')
        print(f'{"Wavelength start [nm]":<25} : {self.configs["w_start"]:<6}')
        print(f'{"Wavelength stop [nm]":<25} : {self.configs["w_stop"]:<6}')
        print(f'{"Sweep step [pm]":<25} : {self.configs["step"]:<6}')

    def dc(self):
        pass

    def ac(self):
        pass

def load_config(ttype):
    fpath = f"{get_config_dirpath()}/{ttype}_config.yaml"
    with open(fpath, 'r') as file:
        configs = yaml.safe_load(file)
    return configs

def print_setup_info(ttype, configs):
    """Print the setup information for each test"""
    print()
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print("----------------------------------------------")
    print("| TEST INFORMATION:                          |")
    print("----------------------------------------------")
    print(f'{"Folder":<25} : {configs["folder"]:<12}')
    print(f'{"Test Type":<25} : {ttype:<12}')
    print_info = PrintSubparserInfo(configs)
    if ttype == "passive":
        print_info.iloss()
    elif ttype == "ac":
        print_info.ac()
    elif ttype == "dc":
        print_info.dc()
    print()


def test_distribution(ttype, configs):
    """ 
    Distribute tests 
        type: test type,
        configs: containing all input arguments
    """
    folder = configs["folder"]
    info = TestInfo()
    addr = get_gpib_full_addr(configs["addr"])

    create_folder(folder)
    
    if ttype == "passive":
        instr = Agilent8163B(addr=addr)
        sweeps = PASILossSweep(instr=instr)
        info.passive(folder, configs)
        sweeps.run_sweep(folder, configs)

    elif ttype == "ac":
        pass
    elif ttype == "dc":
        instr = AgilentE3640A(addr=addr)
        sweeps = DCSweeps(instr=instr)
        info.dc(folder, configs)
        sweeps.run_sweep(chip_name=folder, configs=configs)
        

if __name__ == "__main__":
    version_check()
    
    loglvl = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

    parser = argparse.ArgumentParser(
        description="Automated testing for optical chip", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-t",
        "--test",
        dest="test",
        metavar="",
        nargs=1,
        type=str,
        help="Tests: " + ", ".join([meas for meas in TEST_TYPES]),
        required=True,
    )
    parser.add_argument(
        "--log-lvl",
        dest="loglvl",
        metavar="",
        nargs=1,
        type=str,
        default=["INFO"],
        help=f'Levels: {", ".join([i for i in loglvl])}',
        required=False,
    )

    args = parser.parse_args()

    logging.basicConfig(filename="logging.log",
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=args.loglvl[0])
    
    logger = logging.getLogger()
    cmd = logging.StreamHandler()
    cmd.setFormatter(CustomFormatter())
    logger.addHandler(cmd)

    configs = load_config(args.test)
    print_setup_info(args.test[0], configs)
    test_distribution(args.test[0], configs)
    
    

    

