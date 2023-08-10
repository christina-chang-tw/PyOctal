from lib.util.file_operations import export_to_csv
from lib.util.util import get_func_name, package_info, get_result_dirpath

class TestInfo():
    """
    Sweep Test Information
    """
    @staticmethod
    def passive(chip_name, configs):
        """ Information about passive testing """
        info = {
            "Testing Type" : "Passive insertion Loss",
            "Number of channels" : 1,
            "Power [dBm]" : configs.power,
            "Start wavelength [nm]" : f'{configs.w_start}',
            "Stop wavelength [nm]" : f'{configs.w_stop}',
            "Wavelength step [pm]" : configs.w_step,
            "Lengths [um]" : [", ".join(map(str, configs.lengths))],
        }
        export_to_csv(package_info(info), get_result_dirpath(chip_name), f'{configs.fname}_info')


    @staticmethod
    def dc(chip_name, configs):
        """ Information about dc testing """
        info = {
            "Testing Type" : "DC Scan",
            "Number of channels" : 1,
            "Power [dBm]" : configs.power,
            "Start voltage [V]" : configs.v_start,
            "Stop voltage [V]" : configs.v_stop,
            "Step voltage [V]" : configs.v_step,
        }
        export_to_csv(package_info(info), get_result_dirpath(chip_name), f'{configs.fname}_info')
