import textwrap
import argparse
import logging
import pyvisa
import pickle

from pyoctal.instruments import (
    Agilent8163B, 
    KeysightFlexDCA, 
    KeysightE8257D,
    FiberlabsAMP
)
from pyoctal.util.util import (
    setup_rootlogger,
    load_config
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


INSTR_TYPES = ("agilent8163B", "highigh_speed", "fiberlabsAMP")

class PrintInfo:
    """ 
    Print subparser-dependent information to the CMD output. 
    """
    @staticmethod
    def agilent8163B_print(args):
        logger.info(f'{"Wavelength [nm]":<25} : {args.wavelength[0]:<6}')
        logger.info(f'{"Output power [dBm]":<25} : {args.power[0]:<6}')
        logger.info(f'{"Averaged period [s]":<25} : {args.period[0]:<6}')
        logger.info(f'{"Reset the instrument?":<25} : {args.reset:<6}')

    @staticmethod
    def high_speed_print(args):
        logger.info(f'{"Frequency [GHz]":<25} : {args.freq[0]:<6}')
        logger.info(f'{"Clock divide ratio":<25} : {args.odratio[0]:<6}')


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
    def high_speed_info():
        pass


def setup(ttype, args, addrs):
    rm = pyvisa.ResourceManager()

    configs = load_config(args.filepath[0])
    addrs = configs.INSTR_ADDRS

    if ttype == "agilent8163B":
        PrintInfo.agilent8163B_print(args)
        mm = Agilent8163B(addr=addrs.Agilent8163B_Addr, rm=rm)
        mm.setup(reset=args.reset, wavelength=args.wavelength[0], power=args.power[0], period=args.period[0])

    elif ttype == "high_speed":
        # obtaining the device
        PrintInfo.high_speed_print(args)
        siggen = KeysightE8257D(addr=addrs.KeysightE8257D_Addr, rm=rm)
        osc = KeysightFlexDCA(addr=addrs.KeysightFlexDCA_Addr, rm=rm)
        siggen.set_freq_fixed(freq=args.freq[0])
        osc.lock_clk()
        osc.set_clk_odratio(ratio=args.odratio[0])

    elif ttype == "fiberlabsAMP":
        amp = FiberlabsAMP(addr=addrs.FiberlabsAMP_Addr, rm=rm)
        if args.prediction:
            def predict(model):
                """ Predict the required setting. """
                chan_max = 1048 if args.mode[0] == "ACC" else 10
                # predict the output current
                predicted = model.predict(args.wavelength[0], args.loss[0])

                # # read in a file containing at these two columns with the first two being:
                # # col0: set current/power (user sets this)
                # # col1: output current/power (monitored by the instrument)
                # df = get_dataframe_from_csv(cdiff_fpath)

                # # perform true value and set value mapping
                # row = df.iloc[df[:,1] == output_curr]
                # predicted = df.iloc[row, 0]
                chan = predicted/chan_max

                predicted_str = textwrap.dedent(f"""
                    Required current is {predicted} mA. 
                    Set Channel{chan} to {predicted%chan_max}.
                    Channels smaller than {chan} should be set to {chan_max} and greater set to 0.
                    """)
                return predicted, predicted_str
            with open(args.mfile[0], "rb") as file:
                model = pickle.load(file)
            predicted, predicted_str = predict(model)
            logger.info(predicted_str)
            amp.set_vals_smart(predicted)
        else:
            if args.mode[0] == "ACC":
                amp.set_curr(chan=args.channel[0], curr=args.current[0])
            elif args.mode[0] == "ALC":
                amp.set_power(chan=args.channel[0], power=args.power[0])
    rm.close()



def main():
    parser = argparse.ArgumentParser(
        description="Remote setup the instrument", 
        formatter_class=CustomArgparseFormatter)
    parser.add_argument("-f", "--filepath", type=str, metavar="", dest="filepath", nargs=1, default=("./configs/instr_config.yaml",), help="Path to the configuration file.", required=False)

    subparsers = parser.add_subparsers(
        dest="test",
        help="Test type: " + ", ".join(INSTR_TYPES),
        required=True
    )

    # Subparser arguments for setting up Agilent 8163B
    agilent8163B = subparsers.add_parser(INSTR_TYPES[0], description=SubparserInfo.agilent8163B_info(), help="Multimeter M8163B equipment setup.", formatter_class=CustomArgparseFormatter)
    agilent8163B.add_argument("-w", "--wavelength", type=float, metavar="", dest="wavelength", nargs=1, default=(1550,), help="Sensing and output wavelength [nm].", required=False)
    agilent8163B.add_argument("-p", "--power", type=float, metavar="", dest="power", nargs=1, default=(10,), help="Laser output power [dBm].", required=False)
    agilent8163B.add_argument("-t", "--avg-period", type=float, metavar="", dest="period", nargs=1, default=(200e-03,), help="Averaged period [s].", required=False)
    agilent8163B.add_argument("--reset", action="store_true", dest="reset", help="Reset the instrument")
    
    # Subparser arguments for setting up high-speed testing involving KeysightE8257D and KeysightFlexDCA
    high_speed = subparsers.add_parser(INSTR_TYPES[1], description=SubparserInfo.high_speed_info(), help="High speed instrument setup.", formatter_class=CustomArgparseFormatter)
    high_speed.add_argument("-f", "--frequency", type=float, metavar="", dest="freq", nargs=1, default=(1,), help="Set the frequency of the signal generator [GHz].", required=False)
    high_speed.add_argument("-r", "--odratio", type=str, metavar="", dest="odratio", nargs=1, default=("unit",), help="Set the output clock divide ratio.", required=False)

    fiberlabsAMP = subparsers.add_parser(INSTR_TYPES[2], description=SubparserInfo.agilent8163B_info(), help="Multimeter M8163B equipment setup.", formatter_class=CustomArgparseFormatter)
    fiberlabsAMP.add_argument("--prediction", action="store_true", dest="prediction", help="If present, makes prediction based on the wavelength [nm] and the loss [dB].")
    fiberlabsAMP.add_argument("--mfile", type=str, metavar="", dest="mfile", help='Model file. Required when "prediction" is present.', required=False)
    fiberlabsAMP.add_argument("-w", "--wavelength", type=float, metavar="", dest="wavelength", nargs=1, default=(1550,), help="Wavelength of interest [nm].", required=False)
    fiberlabsAMP.add_argument("-l", "--loss", type=float, metavar="", dest="loss", nargs=1, default=(-10,), help="Loss of interest [dB].", required=False)
    fiberlabsAMP.add_argument("-i", "--current", type=float, metavar="", dest="loss", nargs=1, default=(0,), help="Channel current [mA].", required=False)
    fiberlabsAMP.add_argument("-m", "--mode", type=str, metavar="", dest="mode", nargs=1, default=("ACC",), help="Mode: ALC or ACC.", required=False)
    fiberlabsAMP.add_argument("-c", "--channel", type=int, metavar="", dest="channel", nargs=1, default=(1,), help="Selected channel.", required=False)
    fiberlabsAMP.add_argument("-p", "--power", type=float, metavar="", dest="power", nargs=1, default=(10,), help="Channel power [dBm].", required=False)

    args = parser.parse_args()
    setup(args.test, args, INSTR_ADDRS)



if __name__ == "__main__":
    main()