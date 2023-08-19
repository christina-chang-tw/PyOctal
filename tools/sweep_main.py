import argparse
from datetime import datetime
import logging
import yaml
import pyvisa

from pyoctal.sweeps.info import TestInfo
from pyoctal.sweeps import (
    ILossSweep, 
    DCSweeps,
    IVSweeps,
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


TEST_TYPES = ("passive", "dc", "ac", "iv")


class PrintSubparserInfo():
    """ Print subparser-dependent information to the CMD output """

    @staticmethod
    def passive(configs):
        logger.info(f'{"Output power [dBm]":<25} : {configs.power:<6}')
        logger.info(f'{"Wavelength start [nm]":<25} : {configs.w_start:<6}')
        logger.info(f'{"Wavelength stop [nm]":<25} : {configs.w_stop:<6}')
        logger.info(f'{"Sweep step [pm]":<25} : {configs.w_step:<6}')
        logger.info(f'{"Length [um]":<25} : {", ".join(list(map(str, configs.lengths))) if configs.lengths is not None else ""}')

    @staticmethod
    def dc(configs):
        logger.info(f'{"Output power [dBm]":<25} : {configs.power}')
        logger.info(f'{"Voltage start [dBm]":<25} : {configs.v_start:<6}')
        logger.info(f'{"Voltage stop [nm]":<25} : {configs.v_stop:<6}')
        logger.info(f'{"Voltage step [nm]":<25} : {configs.v_step:<6}')
        logger.info(f'{"Cycle":<25} : {configs.cycle:<6}')
        logger.info(f'{"Wavelength start [nm]":<25} : {configs.w_start:<6}')
        logger.info(f'{"Wavelength stop [nm]":<25} : {configs.w_stop:<6}')
        logger.info(f'{"Wavelength step [nm]":<25} : {configs.w_step:<6}')
        logger.info(f'{"Wavelength speed [nm/s]":<25} : {configs.w_speed:<6}')

    @staticmethod
    def ac(configs):
        pass

    @staticmethod
    def iv(configs):
        logger.info(f'{"Voltage start [dBm]":<25} : {configs.v_start:<6}')
        logger.info(f'{"Voltage stop [nm]":<25} : {configs.v_stop:<6}')
        logger.info(f'{"Voltage step [nm]":<25} : {configs.v_step:<6}')
        logger.info(f'{"Time step [s]":<25} : {configs.t_step:<6}')


def log_setup_info(ttype, configs, ttype_configs):
    end = '\033[0m'
    italic = '\033[3m'
    bold = '\033[1m'
    underline = '\033[4m'
    """Print the setup information for each test"""
    logger.info("")
    logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    logger.info("##############################################")
    logger.info("## TEST INFORMATION:                        ##")
    logger.info("##############################################")
    logger.info("")
    logger.info(underline + bold + italic + "General Variables" + end)
    logger.info(f'{"Folder":<10} : {configs.folder:<12}')
    logger.info(f'{"Filename":<10} : {configs.fname:<12}')
    logger.info(f'{"Test Type":<10} : {ttype:<12}')
    logger.info(f'{"Funcion":<10} : {configs.func:<12}')
    logger.info(f'{"Address":<10} :')
    for instr_type in configs.instr_addrs.keys():
        addr = configs.instr_addrs[instr_type]
        addr_str = ", ".join(addr)
        logger.info(f'  {instr_type:<6} - {len(addr)} - {addr_str}')
    logger.info("")

    logger.info(underline + bold + italic + "Test-Specific Variables" + end)
    if ttype == "passive":
        PrintSubparserInfo.passive(ttype_configs)
    elif ttype == "ac":
        PrintSubparserInfo.ac(ttype_configs)
    elif ttype == "dc":
        PrintSubparserInfo.dc(ttype_configs)
    elif ttype == "iv":
        PrintSubparserInfo.iv(ttype_configs)
    logger.info("")



def load_config(fpath):
    """ Loading the appropriate configuration file for the test. """
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
    rm = pyvisa.ResourceManager()

    # create a folder for the test chip if this has not been done so
    create_folder(folder)
    
    if ttype == "passive":
        TestInfo.passive(folder=folder, fname=configs.fname, ttype_configs=configs.passive)
        sweeps = ILossSweep(
            rm=rm,
            ttype_configs=configs.passive, 
            instr_addrs=configs.instr_addrs,
            folder=configs.folder,
            fname=configs.fname,
            )
        func = getattr(sweeps, configs.func)
        if configs.func == "run_ilme":
            func(configs.passive.lengths)
        else:
            func()

    elif ttype == "ac":
        pass

    elif ttype == "dc":
        TestInfo.dc(folder=folder, fname=configs.fname, ttype_configs=configs.dc)
        sweeps = DCSweeps(
            rm=rm,
            ttype_configs=configs.dc, 
            instr_addrs=configs.instr_addrs,
            folder=configs.folder,
            fname=configs.fname,
        )
        func = getattr(sweeps, configs.func)
        func()

    elif ttype == "iv":
        TestInfo.iv(folder=folder, fname=configs.fname, ttype_configs=configs.iv)
        sweeps = IVSweeps(
            rm=rm,
            ttype_configs=configs.iv, 
            instr_addrs=configs.instr_addrs,
            folder=configs.folder,
            fname=configs.fname,
        )
        func = getattr(sweeps, configs.func)
        func()

        

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

    config_path = "./configs/sweep_config.yaml"
    parser.add_argument(
        "--config-path",
        dest="config_path",
        metavar="",
        nargs=1,
        type=str,
        default=(config_path,),
        help=f'Path to a config file.',
        required=False,
    )

    args = parser.parse_args()
    ttype = args.test[0]

    configs = load_config(args.config_path[0])
    ttype_configs = configs[ttype]
    log_setup_info(ttype, configs, ttype_configs)
    test_distribution(ttype, configs, ttype_configs)
    

if __name__ == "__main__":
    main()
    

