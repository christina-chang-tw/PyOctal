from lib.instruments.agilent8163B import Agilent8163B
from lib.util.util import version_check

import pyvisa
import argparse

INSTR_TYPES = ("m_8163b", )
INSTR_OPERATIONS = {
    INSTR_TYPES[0] : ("setup", ),
}

# Instruments' GPIB address
Agilent8163B_ADDR = "GPIB0::25::INSTR"

def setup(rm, ttype, args):
    if ttype == "m_8163b":
        instr = Agilent8163B(rm=rm, addr=Agilent8163B_ADDR)
        if args.op[0] == "setup":
            instr.setup(wavelength=args.wavelength[0], power=args.power[0])

def print_terminal():
    pass


if __name__ == "__main__":

    version_check()

    parser = argparse.ArgumentParser(
        description="Remote setup the instrument", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(
        dest="test",
        help="Test type: " + ", ".join([meas for meas in INSTR_TYPES]),
        required=True
    )

    m_8163b = subparsers.add_parser(INSTR_TYPES[0], help="Multimeter M8163B Equipment", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    m_8163b.add_argument("-w", "--wavelength", type=float, metavar="", dest="wavelength", nargs=1, default=(1550,), help="Sensing and output wavelength [nm]", required=False)
    m_8163b.add_argument("-p", "--power", type=float, metavar="", dest="power", nargs=1, default=(10,), help="Laser output power [dBm]", required=False)
    m_8163b.add_argument("-o", "--operation", type=str, metavar="", dest="op", nargs=1, default="setup", help=f'Operations: {", ".join(INSTR_OPERATIONS[INSTR_TYPES[0]])}', required=False)
    
    args = parser.parse_args()

    rm = pyvisa.ResourceManager()
    setup(rm, args.test, args)
    rm.close()
