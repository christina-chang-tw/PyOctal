from lib.instruments.multimeter import M_8163B

import pyvisa
import argparse

INSTR_TYPES = ("m_8163b", )


def setup(rm, ttype, args):
    if ttype == "m_8163b":
        instr = M_8163B(rm=rm, addr="GPIB0::28::INSTR")
        instr.setup(wavelength=args.wavelength[0], power=args.power[0])

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Remote setup the instrument", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(
        dest="test",
        help="Test type: " + ", ".join([meas for meas in INSTR_TYPES]),
        required=True
    )

    m_8163b = subparsers.add_parser(INSTR_TYPES[0], help="Multimeter M8163B Equipment", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    m_8163b.add_argument("-w", "--wavelength", type=float, metavar="", dest="wavelength", nargs=1, default=1550, help="Sensing and output wavelength [nm]", required=False)
    m_8163b.add_argument("-p", "--power", type=float, metavar="", dest="power", nargs=1, default=10, help="Laser output power [dBm]", required=False)
    
    args = parser.parse_args()

    rm = pyvisa.ResourceManager()
    setup(rm, args.test, args)
    rm.close()
