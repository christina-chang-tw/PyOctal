from lib.util.csv_operations import export_csv, package_info
from lib.util.util import get_func_name

class TestInfo():
    """ Information about tests that are run and export to an info file in csv format """
    @staticmethod
    def iloss(chip_name, ilme, args):
        info = {
            "Testing Type" : "Insertion Loss",
            "Power [dBm]" : args.power[0],
            "Wavelength range [nm]" : f'{args.range[0]} - {args.range[1]}',
            "Wavelength step [nm]" : args.step[0],
            "Lengths [um]" : [", ".join(str(i)) for i in args.lengths],
            "Number of channels" : ilme.get_no_channels(),
        }
        export_csv(package_info(info), chip_name, f'{args.structure[0]}_{get_func_name()}_info')


    