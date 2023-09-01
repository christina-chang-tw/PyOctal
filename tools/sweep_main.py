import argparse
from datetime import datetime
import logging
import yaml
import pyvisa
from typing import Union

from pyoctal.sweeps import (
    ILossSweep, 
    DCSweeps,
    IVSweeps,
    AMPSweeps
)
from pyoctal.util.formatter import CustomArgparseFormatter
from pyoctal.util.util import (
    create_folder,
    setup_rootlogger,
    package_info,
    DictObj
)
from pyoctal.util.file_operations import export_to_csv

LOG_FNAME = "./logging.log"
root_logger = logging.getLogger()
setup_rootlogger(root_logger, LOG_FNAME)
logger = logging.getLogger(__name__)


TEST_TYPES = ("passive", "dc", "ac", "iv", "amp")


class SweepTestInfo:
    """
    Sweep Test Information
    """
    def __init__(self, folder, fname):
        self.folder = folder
        self.fname = fname

    def passive(self, configs):
        """ Information about passive testing """
        self.fname = self.fname + "_passive_info.csv"
        info = {
            "Power [dBm]" : configs.power,
            "Start wavelength [nm]" : configs.w_start,
            "Stop wavelength [nm]" : configs.w_stop,
            "Wavelength step [pm]" : configs.w_step,
            "Lengths [um]" : [", ".join(map(str, configs.lengths) if configs.lengths is not None else "")],
        }
        return info

    def dc(self, configs):
        """ Information about dc testing """
        self.fname = self.fname + "_dc_info.csv"
        info = {
            "Power [dBm]" : configs.power,
            "Start voltage [V]" : configs.v_start,
            "Stop voltage [V]" : configs.v_stop,
            "Step voltage [V]" : configs.v_step,
            "Cycle" : configs.cycle,
            "Wavelength start [nm]" : configs.w_start,
            "Wavelength stop [nm]" : configs.w_stop,
            "Wavelength step [nm]" : configs.w_step,
            "Scan speed [nm/s]" : configs.w_speed,
        }
        return info

    def iv(self, configs):
        """ Information about iv testing """
        self.fname = self.fname + "_iv_info.csv"
        info = {
            "Start voltage [V]" : configs.v_start,
            "Stop voltage [V]" : configs.v_stop,
            "Step voltage [V]" : configs.v_step,
            "Time step [s]" : configs.t_step,
        }
        return info
    
    def amp(self, configs):
        """ Information about amp testing. """
        self.fname = self.fname + "_amp_info.csv"
        info = {
            "Mode" : configs.mode,
            "Start Value" : configs.start,
            "Stop Value" : configs.stop,
            "Step Value" : configs.step,
            "Channels": ", ".join(list(configs.channels)),
        }
        return info

    @staticmethod
    def print(info):
        for key, value in info.items():
            if isinstance(value, Union[tuple, list]):
                if value is not None:
                    logger.info(f'{key:<25} : {", ".join(value)}')
                else:
                    logger.info(f'{key:<25} :')
            elif isinstance(value, Union[str, float, int]):
                logger.info(f'{key:<25} : {value:}')
            else:
                raise ValueError("Values invalid.")
            
    def export_csv(self, info):
        export_to_csv(data=package_info(info), folder=self.folder, fname=self.fname)


def log_setup_info(ttype, configs, ttype_configs):
    """
    Print the setup information for each test
    """
    end = '\033[0m'
    italic = '\033[3m'
    bold = '\033[1m'
    underline = '\033[4m'
    
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
    testinfo = SweepTestInfo(configs.folder, configs.fname)
    info = []
    if ttype == "passive":
        info = testinfo.passive(ttype_configs)
    elif ttype == "ac":
        pass
    elif ttype == "dc":
        info = testinfo.dc(ttype_configs)
    elif ttype == "iv":
        info = testinfo.iv(ttype_configs)
    elif ttype == "amp":
        info = testinfo.amp(ttype_configs)
    testinfo.print(info)
    testinfo.export_csv(info)
    logger.info("")


def load_config(fpath):
    """ 
    Loading the appropriate configuration file for the test. 
    """
    with open(file=fpath, mode='r') as file:
        configs = yaml.safe_load(file)
    return DictObj(**configs)


def test_distribution(ttype, configs, ttype_configs):
    """ 
    Distribute tests 
        type: test type,
        configs: containing all input arguments
    """
    folder = configs.folder
    # create a folder for the test chip if this has not been done so
    create_folder(folder)
    log_setup_info(ttype, configs, ttype_configs)
    rm = pyvisa.ResourceManager()
    
    if ttype == "passive":
        sweep = ILossSweep(
            rm=rm,
            ttype_configs=ttype_configs, 
            instr_addrs=configs.instr_addrs,
            folder=configs.folder,
            fname=configs.fname,
            )

    elif ttype == "ac":
        pass

    elif ttype == "dc":
        sweep = DCSweeps(
            rm=rm,
            ttype_configs=ttype_configs, 
            instr_addrs=configs.instr_addrs,
            folder=configs.folder,
            fname=configs.fname,
        )

    elif ttype == "iv":
        sweep = IVSweeps(
            rm=rm,
            ttype_configs=ttype_configs, 
            instr_addrs=configs.instr_addrs,
            folder=configs.folder,
            fname=configs.fname,
        )

    elif ttype == "amp":
        sweep = AMPSweeps(
            rm=rm,
            ttype_configs=ttype_configs, 
            instr_addrs=configs.instr_addrs,
            folder=configs.folder,
            fname=configs.fname,
        )

    # run the sweep function
    func = getattr(sweep, configs.func)
    if configs.func == "run_ilme":
        func(configs.passive.lengths)
    else:
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
    test_distribution(ttype, configs, ttype_configs)
    

if __name__ == "__main__":
    main()
    

