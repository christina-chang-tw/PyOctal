from lib.info import TestInfo
from lib.sweeps.iloss import ILossSweep
from lib.instruments.pas import ILME
from lib.instruments.multimeter import M_8163B
from lib.util.csv_operations import create_folder
from lib.util.logger import CustomFormatter
from lib.util.util import version_check

import argparse
from datetime import datetime
import logging
import pyvisa

TEST_TYPES = ("iloss", "dc", "ac")

class Subparsers():
    """ Adding subparser-dependent arguments"""

    @staticmethod
    def iloss(parser):
        requiredNamed = parser.add_argument_group('required arguments')
        requiredNamed.add_argument("-l", "--lengths", type=float, metavar="", dest="lengths", nargs="+", help="The lengths of each test waveguides", required=True)
        parser.add_argument("-p", "--power", type=float, metavar="", dest="power", nargs=1, default=[10], help="laser output power [dBm]", required=False)
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
        print(f'{"Length [um]":<25} : {", ".join([str(round(i, 2)) for i in self.args.lengths])}')
        print(f'{"Output power [dBm]":<25} : {self.args.power[0]:<6}')
        print(f'{"Wavelength Range [nm]":<25} : {self.args.range[0]:<3} - {self.args.range[1]:<3}')
        print(f'{"Sweep step [pm]":<25} : {self.args.step[0]:<6}')

    def dc(self):
        pass

    def ac(self):
        pass


def print_setup_info(ttype, args):
    """Print the setup information for each test"""

    print()
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print("----------------------------------------------")
    print("| TEST INFORMATION:                          |")
    print("----------------------------------------------")
    print(f'{"Chip name":<25} : {args.chip_name[0]:<12}')
    print(f'{"Test Type":<25} : {ttype:<12}')
    print_info = PrintSubparserInfo(args)
    if ttype == "iloss":
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
    create_folder(args.chip_name[0])
    rm = pyvisa.ResourceManager()
    info = TestInfo()
    pal = ILME()
    

    if ttype == "iloss":
        M_8163B_ADDR = "GPIB0::25::INSTR"
        instr = M_8163B(rm=rm, addr=M_8163B_ADDR)
        sweeps = ILossSweep(pal, instr)
        info.iloss(args.chip_name[0], args)
        sweeps.iloss(args.chip_name[0], args)

    elif ttype == "ac":
        pass
    elif ttype == "dc":
        pass



if __name__ == "__main__":
    version_check()
    
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
        default=["XXX"],
        help="Chip name",
        required=False,
    ) # this create a folder in the name of the chip under test folder
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
    subparsers = parser.add_subparsers(
        dest="test",
        help="Test type: " + ", ".join([meas for meas in TEST_TYPES]),
        required=True,
    )
    

    # Arguments for passive testing
    iloss = subparsers.add_parser(TEST_TYPES[0], help="insertion loss testing", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    dc = subparsers.add_parser(TEST_TYPES[1], help="dc testing", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ac = subparsers.add_parser(TEST_TYPES[2], help="ac testing", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Add parser-specfic arguments
    Subparsers.iloss(iloss)
    Subparsers.dc(dc)
    Subparsers.ac(ac)

    args = parser.parse_args()

    logging.basicConfig(filename="logging.log",
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=args.loglvl[0])
    
    logger = logging.getLogger()
    cmd = logging.StreamHandler()
    cmd.setFormatter(CustomFormatter())
    logger.addHandler(cmd)

    print_setup_info(args.test, args)
    test_distribution(args.test, args)

    

