from lib.util.file_operations import export_to_csv, package_info
from lib.util.util import get_func_name

class TestInfo():
    """ Information about tests that are run and export to an info file in csv format """
    @staticmethod
    def passive(chip_name, ilme, configs):
        info = {
            "Testing Type" : "Passive insertion Loss",
            "Number of channels" : ilme.get_no_channels(),
            "Power [dBm]" : configs["power"],
            "Start wavelength [nm]" : f'{configs["w_start"]}',
            "Stop wavelength [nm]" : f'{configs["w_stop"]}',
            "Wavelength step [pm]" : configs["step"],
            "Lengths [um]" : [", ".join(str(i)) for i in configs.lengths],
        }
        export_to_csv(package_info(info), chip_name, f'{configs["structure"]}_{get_func_name()}_info')


    @staticmethod
    def dc(chip_name, ilme, configs):
        info = {
            "Testing Type" : "DC Scan",
            "Number of channels" : ilme.get_no_channels(),
            "Power [dBm]" : configs["power"],
            "Start voltage [V]" : configs["v_start"],
            "Stop voltage [V]" : configs["v_stop"],
            "Step voltage [V]" : configs["v_step"],
        }
        export_to_csv(package_info(info), chip_name, f'{configs["structure"]}_{get_func_name()}_info')
