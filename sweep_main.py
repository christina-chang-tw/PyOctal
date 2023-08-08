# Perform version check before everything
from lib.util.util import pyversion_check, platform_check, get_callable_funcs
platform_check()
pyversion_check()

from lib.sweeps.info import TestInfo
from lib.sweeps import (
    ILossSweep, 
    DCSweeps,
    ACSweeps,
)
from lib.instruments import (
    Agilent8163B, 
    AgilentE3640A,
)
from lib.util.formatter import CustomLogFormatter, CustomArgparseFormatter
from lib.util.util import (
    get_config_dirpath, 
    create_folder,
    get_result_dirpath
)

import argparse
from datetime import datetime
import logging
import yaml

TEST_TYPES = ("passive", "dc", "ac")


class PrintSubparserInfo():
    """ Print subparser-dependent information to the CMD output """

    def __init__(self, configs):
        self.configs = configs

    def passive(self):
        print(f'{"Length [um]":<25} : {", ".join([str(round(i, 2)) for i in self.configs["lengths"]])}')
        print(f'{"Output power [dBm]":<25} : {self.configs["power"]:<6}')
        print(f'{"Wavelength start [nm]":<25} : {self.configs["w_start"]:<6}')
        print(f'{"Wavelength stop [nm]":<25} : {self.configs["w_stop"]:<6}')
        print(f'{"Sweep step [pm]":<25} : {self.configs["step"]:<6}')

    def dc(self):
        pass

    def ac(self):
        pass

def print_setup_info(ttype, configs):
    """Print the setup information for each test"""
    print()
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print("##############################################")
    print("## TEST INFORMATION:                        ##")
    print("##############################################")
    print()
    print(f'{"Folder":<10} : {configs["folder"]:<12}')
    print(f'{"Test Type":<10} : {ttype:<12}')
    print("-------------------------------------------")
    print(f'| {"Dev. Types":<10} | {"No. Dev.":^8} | {"Addresses":<15} |')
    print("-------------------------------------------")
    for instr_type in configs["instr_addr"].keys():
        address = configs["instr_addr"][instr_type]
        print(f'| {instr_type:<10} | {len(address):^8} | {address}')
    print("-------------------------------------------")
    print()

    print_info = PrintSubparserInfo(configs)
    if ttype == "passive":
        print_info.passive()
    elif ttype == "ac":
        print_info.ac()
    elif ttype == "dc":
        print_info.dc()
    print()


def load_config(ttype, args_config):
    #  If a config file is defined by user then use that otherwise use the default ones
    fpath = f"{get_config_dirpath()}/{ttype}_config.yaml" if args_config is None else args_config[0]
    with open(fpath, 'r') as file:
        configs = yaml.safe_load(file)
    return configs


def test_distribution(ttype, configs):
    """ 
    Distribute tests 
        type: test type,
        configs: containing all input arguments
    """
    folder = configs["folder"]
    instr_addrs = configs["instr_addrs"]
    info = TestInfo()

    # create a folder for the test chip if this has not been done so
    create_folder(get_result_dirpath(folder))
    
    if ttype == "passive":
        sweeps = ILossSweep(instr_addrs=instr_addrs)
        info.passive(folder, configs)
        sweeps.run_sweep_ilme(folder, configs)

    elif ttype == "ac":
        pass
    elif ttype == "dc":
        sweeps = DCSweeps(instr_addrs=instr_addrs)
        info.dc(folder, configs)
        sweeps.run_sweep_ilme(chip_name=folder, configs=configs)
        

def main():
    loglvl = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

    desc = """
Automated Sweep Testing for Optical Chips

Example:
Run a dc sweep test with logging level as DEBUG and specify a path for a config file
    
    > python -m sweep_main -t dc --log-lvl DEBUG --config ./config/<fname>.yaml
    """

    parser = argparse.ArgumentParser(
        description=desc, 
        formatter_class=CustomArgparseFormatter)
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

    parser.add_argument(
        "--config",
        dest="config",
        metavar="",
        nargs=1,
        type=str,
        default=None,
        help=f'Setting a user-defined path to a config file',
        required=False,
    )

    args = parser.parse_args()
    ttype = args.test[0]

    logging.basicConfig(filename="logging.log",
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=args.loglvl[0])
    
    logger = logging.getLogger()
    cmd = logging.StreamHandler()
    cmd.setFormatter(CustomLogFormatter())
    logger.addHandler(cmd)

    configs = load_config(ttype, args.config)
    print_setup_info(ttype, configs)
    test_distribution(ttype, configs)
    

if __name__ == "__main__":
    main()
    

