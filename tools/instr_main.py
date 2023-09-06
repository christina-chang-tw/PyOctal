import textwrap
import argparse
import logging
import pyvisa
import pickle

from pyoctal.instruments import (
    Agilent8163B, 
    Agilent8164B,
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


INSTR_TYPES = ("agilent816xB", "highigh_speed", "fiberlabsAMP")

class PrintInfo:
    """ 
    Print subparser-dependent information to the CMD output. 
    """
    @staticmethod
    def agilent816xB_print(args):
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
    def agilent816xB_info() -> str:
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

    @staticmethod
    def fiberlabsAMP():
        pass


def setup(instr, configs):
    rm = pyvisa.ResourceManager()

    instr_configs = configs[instr]
    addrs = configs.instr_addrs

    if instr == "agilent816xB":
        if instr_configs.model[0] == "8163":  
            PrintInfo.agilent816xB_print(instr_configs)
            mm = Agilent8163B(addr=addrs.Agilent816xB_Addr, rm=rm)
            mm.setup(reset=instr_configs.reset, wavelength=instr_configs.wavelength[0], power=instr_configs.power[0], period=instr_configs.period[0])
        elif instr_configs.model[0] == "8164":
            PrintInfo.agilent816xB_print(instr_configs)
            mm = Agilent8164B(addr=addrs.Agilent816xB_Addr, rm=rm)
            mm.setup(reset=instr_configs.reset, wavelength=instr_configs.wavelength[0], power=instr_configs.power[0], period=instr_configs.period[0])


    elif instr == "high_speed":
        # obtaining the device
        PrintInfo.high_speed_print(instr_configs)
        siggen = KeysightE8257D(addr=addrs.KeysightE8257D_Addr, rm=rm)
        osc = KeysightFlexDCA(addr=addrs.KeysightFlexDCA_Addr, rm=rm)
        siggen.set_freq_fixed(freq=instr_configs.freq[0])
        osc.lock_clk()
        osc.set_clk_odratio(ratio=instr_configs.odratio[0])

    elif instr == "fiberlabsAMP":
        amp = FiberlabsAMP(addr=addrs.FiberlabsAMP_Addr, rm=rm)
        if instr_configs.prediction:
            def predict(model):
                """ Predict the required setting. """
                chan_max = 1048 if instr_configs.mode[0] == "ACC" else 10
                # predict the output current
                predicted = model.predict(instr_configs.wavelength[0], instr_configs.loss[0])

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
            with open(instr_configs.mfile[0], "rb") as file:
                model = pickle.load(file)
            predicted, predicted_str = predict(model)
            logger.info(predicted_str)
            amp.set_vals_smart(predicted)
        else:
            if instr_configs.mode[0] == "ACC":
                amp.set_curr(chan=instr_configs.channel[0], curr=instr_configs.current[0])
            elif instr_configs.mode[0] == "ALC":
                amp.set_power(chan=instr_configs.channel[0], power=instr_configs.power[0])
    rm.close()



def main():
    parser = argparse.ArgumentParser(
        description="Remote setup the instrument", 
        formatter_class=CustomArgparseFormatter
    )
    parser.add_argument("--instr", type=str, metavar="", dest="instr", nargs=1, help=f'Instruments: {"".join(INSTR_TYPES)}', required=True)
    parser.add_argument("-f", "--filepath", type=str, metavar="", dest="filepath", nargs=1, default=("./configs/instr_config.yaml",), help="Path to the configuration file.", required=False)

    args = parser.parse_args()

    configs = load_config(args.filepath[0])
    setup(args.instr, configs)



if __name__ == "__main__":
    main()