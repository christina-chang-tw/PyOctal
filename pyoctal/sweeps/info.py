from pyoctal.util.file_operations import export_to_csv
from pyoctal.util.util import package_info

class TestInfo():
    """
    Sweep Test Information
    """
    @staticmethod
    def passive(folder, fname, ttype_configs):
        """ Information about passive testing """
        info = {
            "Testing Type" : "Passive insertion Loss",
            "Number of channels" : 1,
            "Power [dBm]" : ttype_configs.power,
            "Start wavelength [nm]" : f'{ttype_configs.w_start}',
            "Stop wavelength [nm]" : f'{ttype_configs.w_stop}',
            "Wavelength step [pm]" : ttype_configs.w_step,
            "Lengths [um]" : [", ".join(map(str, ttype_configs.lengths))],
        }
        export_to_csv(data=package_info(info), folder=folder, fname=f'{fname}_info.csv')


    @staticmethod
    def dc(folder, fname, ttype_configs):
        """ Information about dc testing """
        info = {
            "Testing Type" : "DC Scan",
            "Number of channels" : 1,
            "Power [dBm]" : ttype_configs.power,
            "Start voltage [V]" : ttype_configs.v_start,
            "Stop voltage [V]" : ttype_configs.v_stop,
            "Step voltage [V]" : ttype_configs.v_step,
            "Cycle" : ttype_configs.cycle,
            "Wavelength start [nm]" : ttype_configs.w_start,
            "Wavelength stop [nm]" : ttype_configs.w_stop,
            "Wavelength step [nm]" : ttype_configs.w_step,
            "Wavelength scan speed [nm/s]" : ttype_configs.w_speed,
        }
        export_to_csv(data=package_info(info), folder=folder, fname=f'{fname}_info.csv')


    @staticmethod
    def iv(folder, fname, ttype_configs):
        """ Information about iv testing """
        info = {
            "Testing Type" : "IV Scan",
            "Number of channels" : 1,
            "Power [dBm]" : ttype_configs.power,
            "Start voltage [V]" : ttype_configs.v_start,
            "Stop voltage [V]" : ttype_configs.v_stop,
            "Step voltage [V]" : ttype_configs.v_step,
        }
        export_to_csv(data=package_info(info), folder=folder, fname=f'{fname}_info.csv')
