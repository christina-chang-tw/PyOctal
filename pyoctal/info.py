import logging
from typing import Union

from pyoctal.util.file_operations import export_to_csv
from pyoctal.util.util import package_info

logger = logging.getLogger(__name__)

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