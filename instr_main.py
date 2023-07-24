# Perform version check before everything
from lib.util.util import pyversion_check
pyversion_check()

from lib.instruments import (
    Agilent8163B, 
    Keysight86100D, 
    KeysightE8257D,
)
from lib.util.util import (
    get_gpib_full_addr, 
    get_config_dirpath,
)
from lib.util.formatter import CustomArgparseFormatter

import textwrap
import argparse

INSTR_TYPES = ("m_8163b", "h_speed")

# Define each instrument's address
Agilent8163B_ADDR = 25
Keysight86100D_ADDR = 1
KeysightE8257D_ADDR = 1


def setup(ttype, args):
    if ttype == "m_8163b":
        instr = Agilent8163B(addr=get_gpib_full_addr(Agilent8163B_ADDR))
        instr.setup(wavelength=args.wavelength[0], power=args.power[0], time=args.period[0])

    elif ttype == "h_speed":
        # obtaining the device
        siggen = KeysightE8257D(addr=get_gpib_full_addr(KeysightE8257D_ADDR))
        osc = Keysight86100D(addr=get_gpib_full_addr(Keysight86100D_ADDR))
        siggen.set_freq(freq=args.freq[0])

        


def subparser_info(type):
    if type == INSTR_TYPES[0]:
        info = textwrap.dedent("""\
                Multimeter M8163B Equipment:

                This is created solely for setting up the device
                
                Example.
                Set the multimeter's output power to 10dBm and wavelength to 1550nm with the measurement averaged period is 200ms.
                
                    > python -m instr_main m_8163b -w 1550 --power 10 -t 200e-03
                
                """)
    
    return info


if __name__ == "__main__":
    config_fpath= f'{get_config_dirpath()}/instr_config.yaml'

    parser = argparse.ArgumentParser(
        description="Remote setup the instrument", 
        formatter_class=CustomArgparseFormatter)

    subparsers = parser.add_subparsers(
        dest="test",
        help="Test type: " + ", ".join([meas for meas in INSTR_TYPES]),
        required=True
    )

    m_8163b = subparsers.add_parser(INSTR_TYPES[0], description=subparser_info("m_8163b"), help="Multimeter M8163B equipment setup", formatter_class=CustomArgparseFormatter)
    m_8163b.add_argument("-w", "--wavelength", type=float, metavar="", dest="wavelength", nargs=1, default=(1550,), help="Sensing and output wavelength [nm]", required=False)
    m_8163b.add_argument("-p", "--power", type=float, metavar="", dest="power", nargs=1, default=(10,), help="Laser output power [dBm]", required=False)
    m_8163b.add_argument("-t", "--avg-time", type=float, metavar="", dest="period", nargs=1, default=(10,), help="Averaged period [s]", required=False)
    
    h_speed = m_8163b = subparsers.add_parser(INSTR_TYPES[0], description=subparser_info("h_speed"), help="High speed instrument setup", formatter_class=CustomArgparseFormatter)
    h_speed.add_argument("-f", "--frequency", type=float, metavar="", dest="freq", nargs=1, default=(1,), help="Set the frequency of the signal generator [GHz]", required=False)

    args = parser.parse_args()


    setup(args.test, args)
