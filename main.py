from lib.info import Test_Info
from lib.sweeps import Sweeps
from lib.instruments.pas import ILME
from lib.csv_operations import create_folder

import argparse
from datetime import datetime
import logging


TEST_TYPES = ("passive", "dc", "ac")

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class Subparsers():
    """ Adding subparser-dependent arguments"""

    @staticmethod
    def iloss(parser):
        requiredNamed = parser.add_argument_group('required arguments')
        requiredNamed.add_argument("-l", "--lengths", type=float, metavar="", dest="lengths", nargs="+", help="The lengths of each test waveguides", required=True)
        parser.add_argument("-p", "--power", type=float, metavar="", dest="power", nargs=1, default=[10], help="laser output power [dBm]", required=False)
        parser.add_argument("-r", "--wavelength-range", type=float, metavar="", dest="range", nargs="+", default=[1540,1570], help="start wavelength and stop wavelength in nm", required=False)
        parser.add_argument("-s", "--sweep-step", type=float, metavar="", dest="step", nargs=1, default=[5], help="Sweep step [nm]", required=False)

    @staticmethod
    def dc(parser):
        pass

    @staticmethod
    def ac(parser):
        pass


class PrintSubparserInfo():
    """ Print subparser-dependent information to the CMD output """

    def __init__(self, args):
        self.args = args

    def iloss(self):
        print(f'{"Lengths":<20} : {[" ".join(str(i)) for i in self.args.lengths]}')
        print(f'{"Output power":<20} : {self.args.power[0]:<6} dB')
        print(f'{"Wavelength Range":<20} : {self.args.range[0]:<3} nm - {self.args.range[1]:<3} nm')
        print(f'{"Sweep step":<20} : {self.args.step[0]:<6} nm/s')

    def dc(self):
        pass

    def ac(self):
        pass


def print_setup_info(ttype, args):
    """Print the setup information for each test"""

    print("Optical testing\n")
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print("---------------------------------------")
    print("| General INFORMATION:                |")
    print("---------------------------------------")
    print(f'{"Chip name":<20} : {args.chip_name:<12}')
    print()
    print("---------------------------------------")
    print("| SETUP PARAMETERS:                   |")
    print("---------------------------------------")
    print(f'{"Test Type":<20} : {ttype:<12}')
    print_info = PrintSubparserInfo(args)
    if ttype == "passive":
        print_info.iloss()
    elif ttype == "ac":
        print_info.ac()
    elif ttype == "dc":
        print_info.dc()
    print()

def test_distribution(ttype, args):
    """ 
    Distributing tests 
        type: test type,
        args: containing all input arguments
    """
    create_folder()
    info = Test_Info()
    pal = ILME()
    sweeps = Sweeps(pal)

    if ttype == "passive":
        info.iloss(args.chip_name, args)
        sweeps.iloss(args.chip_name, args)

    elif ttype == "ac":
        pass
    elif ttype == "dc":
        pass



if __name__ == "__main__":
    loglvl = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

    parser = argparse.ArgumentParser(
        description="Automated testing for optical chip", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-chip", 
        "--chip_name", 
        dest="chip_name",
        metavar="",
        nargs=1,
        type=str,
        default="XXX",
        help="Chip name",
        required=False,
    ) # this create a folder in the name of the chip under test folder
    parser.add_argument(
        "--log-lvl",
        dest="loglvl",
        metavar="",
        nargs=1,
        type=str,
        default="WARNING",
        help=f'Levels: {", ".join([i for i in loglvl])}',
        required=False,
    )
    subparsers = parser.add_subparsers(
        dest="test",
        help="Test type: " + ", ".join([meas for meas in TEST_TYPES]),
        required=True,
    )
    

    # Arguments for passive testing
    iloss = subparsers.add_parser(TEST_TYPES[0], help="passive testing", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    dc = subparsers.add_parser(TEST_TYPES[1], help="dc testing", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ac = subparsers.add_parser(TEST_TYPES[2], help="ac testing", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Add parser-specfic arguments
    Subparsers.iloss(iloss)
    Subparsers.dc(dc)
    Subparsers.ac(ac)

    args = parser.parse_args()

    logging.basicConfig(filename="logging",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=args.loglvl[0])
    
    logger = logging.getLogger()
    cmd = logging.StreamHandler()
    cmd.setFormatter(CustomFormatter())
    logger.addHandler(cmd)

    print_setup_info(args.test, args)
    test_distribution(args.test, args)

    

