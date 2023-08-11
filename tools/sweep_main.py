# Perform version check before everything
from pyoctal.util.util import pyversion_check, platform_check
platform_check()
pyversion_check()

import argparse
from datetime import datetime
import logging
import yaml

from pyoctal.sweeps.info import TestInfo
from pyoctal.sweeps import (
    ILossSweep, 
    DCSweeps,
)
from pyoctal.util.formatter import CustomArgparseFormatter
from pyoctal.util.util import (
    create_folder,
    setup_rootlogger,
    DictObj
)

LOG_FNAME = "./logging.log"
root_logger = logging.getLogger()
setup_rootlogger(root_logger, LOG_FNAME)
logger = logging.getLogger(__name__)


TEST_TYPES = ("passive", "dc", "ac")


class PrintSubparserInfo():
    """ Print subparser-dependent information to the CMD output """

    @staticmethod
    def passive(configs):
        logger.info(f'{"Length [um]":<25} : {", ".join([str(round(i, 2)) for i in configs.lengths])}')
        logger.info(f'{"Output power [dBm]":<25} : {configs.power:<6}')
        logger.info(f'{"Wavelength start [nm]":<25} : {configs.w_start:<6}')
        logger.info(f'{"Wavelength stop [nm]":<25} : {configs.w_stop:<6}')
        logger.info(f'{"Sweep step [pm]":<25} : {configs.w_step:<6}')

    @staticmethod
    def dc(configs):
        pass

    @staticmethod
    def ac(configs):
        pass


def log_setup_info(ttype, configs):
    """Print the setup information for each test"""
    logger.info()
    logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    logger.info("##############################################")
    logger.info("## TEST INFORMATION:                        ##")
    logger.info("##############################################")
    logger.info()
    logger.info(f'{"Folder":<10} : {configs.folder:<12}')
    logger.info(f'{"Test Type":<10} : {ttype:<12}')
    logger.info("-------------------------------------------")
    logger.info(f'| {"Dev. Types":<10} | {"No. Dev.":^8} | {"Addresses":<15} |')
    logger.info("-------------------------------------------")
    for instr_type in configs.instr_addr.keys():
        address = configs.instr_addr[instr_type]
        logger.info(f'| {instr_type:<10} | {len(address):^8} | {address}')
    logger.info("-------------------------------------------")
    logger.info()

    if ttype == "passive":
        PrintSubparserInfo.passive(configs)
    elif ttype == "ac":
        PrintSubparserInfo.ac(configs)
    elif ttype == "dc":
        PrintSubparserInfo.dc(configs)
    logger.info()



def load_config(ttype, args_config):
    #  If a config file is defined by user then use that otherwise use the default ones
    fpath = f"./config/{ttype}_config.yaml" if args_config is None else args_config[0]
    with open(file=fpath, mode='r') as file:
        configs = yaml.safe_load(file)
    return DictObj(**configs)


def test_distribution(ttype, configs):
    """ 
    Distribute tests 
        type: test type,
        configs: containing all input arguments
    """
    folder = configs.folder

    # create a folder for the test chip if this has not been done so
    create_folder(folder)
    
    if ttype == "passive":
        sweeps = ILossSweep(configs=configs)
        TestInfo.passive(folder, configs)
        sweeps.run_ilme(configs.lengths)

    elif ttype == "ac":
        pass
    elif ttype == "dc":
        sweeps = DCSweeps(configs=configs)
        TestInfo.dc(folder, configs)
        sweeps.run_ilme()
        

def main():
    """ Run this when this file is called. """

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
        help="Tests: " + ", ".join(TEST_TYPES),
        required=True,
    )

    parser.add_argument(
        "--config",
        dest="config",
        metavar="",
        nargs=1,
        type=str,
        default=None,
        help='Setting a user-defined path to a config file. Without specified, it is default to ./config/<test>_config.yaml',
        required=False,
    )

    args = parser.parse_args()
    ttype = args.test[0]

    configs = load_config(ttype, args.config)
    log_setup_info(ttype, configs)
    test_distribution(ttype, configs)
    

if __name__ == "__main__":
    main()
    

