import textwrap
import argparse
import logging
import pyvisa

from pyoctal.instruments import (
    Agilent8163B, 
    KeysightFlexDCA, 
    KeysightE8257D,
)
from pyoctal.util.util import (
    setup_rootlogger,
)
from pyoctal.util.formatter import CustomArgparseFormatter


LOG_FNAME = "./logging.log"
root_logger = logging.getLogger()
setup_rootlogger(root_logger, LOG_FNAME)
logger = logging.getLogger(__name__)


###########################################################
### USER DEFINED VARIABLES ################################
# ONLY MODIFY THIS SECTION!                               #
#                                                         #
## Addresses of each devices  #############################
# NOTE: You only have to set the correct address for      #
# instruments related to your operations                  #
#                                                         #
# e.g. Each of the x should be replaced                   #
#   GPIB Device = GPIBx::x::INSTR                         #
#   COM  Device = COMx                                    #     
###########################################################
                                                          
INSTR_ADDRS = {                                               
    "Agilent8163B_Addr": "GPIB0::25::INSTR",              
    "KeysightE8257D_Addr": "",   
    "KeysightFlexDCA_Addr": "",
    "Keysight86100D_Addr": "",                            
}                                                         
###########################################################
###########################################################


INSTR_TYPES = ("agilent8163B", "h_speed")

        
class SubparserInfo:
    @staticmethod
    def agilent8163B_info() -> str:
        info = textwrap.dedent("""
                Multimeter M8163B Equipment:

                This is created solely for setting up the device
                
                E.g.
                Reset the instrument first and set the multimeter's output power to 10dBm and wavelength 
                to 1550nm with the measurement averaged period is 200ms.
                
                    > python -m instr_main agilent8163B -w 1550 --power 10 -t 200e-03 --reset
                
                """)
        return info
    
    @staticmethod
    def agilent8163B_print(args):
        logger.info(f'{"Wavelength [nm]":<25} : {args.wavelength[0]:<6}')
        logger.info(f'{"Output power [dBm]":<25} : {args.power[0]:<6}')
        logger.info(f'{"Averaged period [s]":<25} : {args.period[0]:<6}')
        logger.info(f'{"Reset the instrument?":<25} : {args.reset:<6}')


    @staticmethod
    def h_speed_info():
        pass

    @staticmethod
    def h_speed_print(args):
        logger.info(f'{"Frequency [GHz]":<25} : {args.freq[0]:<6}')
        logger.info(f'{"Clock divide ratio":<25} : {args.odratio[0]:<6}')


def setup(ttype, args, addrs):
    rm = pyvisa.ResourceManager()
    if ttype == "agilent8163B":
        SubparserInfo.agilent8163B_print(args)
        instr = Agilent8163B(addr=addrs["Agilent8163B_Addr"], rm=rm)
        instr.setup(reset=args.reset, wavelength=args.wavelength[0], power=args.power[0], period=args.period[0])

    elif ttype == "h_speed":
        # obtaining the device
        SubparserInfo.h_speed_print(args)
        siggen = KeysightE8257D(addr=addrs["KeysightE8257D_Addr"], rm=rm)
        osc = KeysightFlexDCA(addr=addrs["KeysightFlexDCA_Addr"], rm=rm)
        siggen.set_freq_fixed(freq=args.freq[0])
        osc.lock_clk()
        osc.set_clk_odratio(ratio=args.odratio[0])
    rm.close()

def main():

    parser = argparse.ArgumentParser(
        description="Remote setup the instrument", 
        formatter_class=CustomArgparseFormatter)

    subparsers = parser.add_subparsers(
        dest="test",
        help="Test type: " + ", ".join(INSTR_TYPES),
        required=True
    )

    # Subparser arguments for setting up Agilent 8163B
    agilent8163B = subparsers.add_parser(INSTR_TYPES[0], description=SubparserInfo.agilent8163B_info(), help="Multimeter M8163B equipment setup", formatter_class=CustomArgparseFormatter)
    agilent8163B.add_argument("-w", "--wavelength", type=float, metavar="", dest="wavelength", nargs=1, default=(1550,), help="Sensing and output wavelength [nm]", required=False)
    agilent8163B.add_argument("-p", "--power", type=float, metavar="", dest="power", nargs=1, default=(10,), help="Laser output power [dBm]", required=False)
    agilent8163B.add_argument("-t", "--avg-period", type=float, metavar="", dest="period", nargs=1, default=(200e-03,), help="Averaged period [s]", required=False)
    agilent8163B.add_argument("--reset", action="store_true", dest="reset", help="Reset the instrument")
    
    # Subparser arguments for setting up high-speed testing involving KeysightE8257D and KeysightFlexDCA
    h_speed = subparsers.add_parser(INSTR_TYPES[1], description=SubparserInfo.h_speed_info(), help="High speed instrument setup", formatter_class=CustomArgparseFormatter)
    h_speed.add_argument("-f", "--frequency", type=float, metavar="", dest="freq", nargs=1, default=(1,), help="Set the frequency of the signal generator [GHz]", required=False)
    h_speed.add_argument("-r", "--odratio", type=str, metavar="", dest="odratio", nargs=1, default=("unit",), help="Set the output clock divide ratio", required=False)

    args = parser.parse_args()
    setup(args.test, args, INSTR_ADDRS)



if __name__ == "__main__":
    main()