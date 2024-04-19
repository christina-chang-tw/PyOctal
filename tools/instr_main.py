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
from pyoctal.utils.util import (
    setup_rootlogger,
    load_config
)
from pyoctal.utils.formatter import CustomArgparseFormatter


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
                                                          
addrs = {                                               
    "Agilent8163B_Addr": "GPIB0::25::INSTR",              
    "KeysightE8257D_Addr": "",   
    "KeysightFlexDCA_Addr": "",
    "Keysight86100D_Addr": "",                            
}                                                         
###########################################################
###########################################################


INSTR_TYPES = ("agilent816xB", "high_speed", "fiberlabsAMP")

class PrintInfo:
    """ 
    Print subparser-dependent information to the CMD output. 
    """
    @staticmethod
    def agilent816xB_print(args):
        logger.info(f'{"Wavelength [nm]":<25} : {args.wavelength:<6}')
        logger.info(f'{"Output power [dBm]":<25} : {args.power:<6}')
        logger.info(f'{"Averaged period [s]":<25} : {args.period:<6}')
        logger.info(f'{"Reset the instrument?":<25} : {args.reset:<6}')

    @staticmethod
    def agilent816xB_op_print(args):
        logger.info(f"{'Target power level [dB]':<25} : {args.db:<6}")
        logger.info(f"{'Target wavelength [nm]':<25} : {args.target:<6}")
        logger.info(f"{'Wavelength range [nm]':<25} : {args.target - args.xrange/2} - {args.target + args.xrange/2}")
        logger.info(f"{'Wavelength step [nm]':<25} : {args.step:<6}")

    @staticmethod
    def high_speed_print(args):
        logger.info(f'{"Frequency [GHz]":<25} : {args.freq:<6}')
        logger.info(f'{"Clock divide ratio":<25} : {args.odratio:<6}')


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
    addrs = configs.addrs

    if instr == "agilent816xB":
        if instr_configs.model == "8163":  
            cls = Agilent8163B
        elif instr_configs.model == "8164":
            cls = Agilent8164B
        mm = cls(addr=addrs.Agilent816xB_Addr, rm=rm)

        if instr_configs.get("op") and instr_configs.op.keys() is not None:
            PrintInfo.agilent816xB_op_print(instr_configs.op)
            wavelength = mm.find_op_wavelength(**instr_configs.op)
            mm.setup(reset=instr_configs.reset, wavelength=wavelength, power=instr_configs.power, period=instr_configs.period)

        else:
            PrintInfo.agilent816xB_print(instr_configs)
            mm.setup(reset=instr_configs.reset, wavelength=instr_configs.wavelength, power=instr_configs.power, period=instr_configs.period)


    elif instr == "high_speed":
        # obtaining the device
        PrintInfo.high_speed_print(instr_configs)
        siggen = KeysightE8257D(addr=addrs.KeysightE8257D_Addr, rm=rm)
        osc = KeysightFlexDCA(addr=addrs.KeysightFlexDCA_Addr, rm=rm)
        siggen.set_freq_fixed(freq=instr_configs.freq)
        osc.lock_clk()
        osc.set_clk_odratio(ratio=instr_configs.odratio)

    elif instr == "fiberlabsAMP":
        amp = FiberlabsAMP(addr=addrs.FiberlabsAMP_Addr, rm=rm)
        if instr_configs.prediction:
            def predict(model):
                """ Predict the required setting. """
                chan_max = amp.chan_curr_max if instr_configs.mode == "ACC" else amp.chan_power_max
                # predict the output current
                predicted = model.predict(instr_configs.wavelength, instr_configs.loss)
                chan = predicted/chan_max

                predicted_str = textwrap.dedent(f"""
                    Required current is {predicted} mA. 
                    Set Channel{chan} to {predicted%chan_max}.
                    Channels smaller than {chan} should be set to {chan_max} and greater set to 0.
                    """)
                return predicted, predicted_str
            with open(instr_configs.mfile, "rb") as file:
                model = pickle.load(file)
            predicted, predicted_str = predict(model)
            logger.info(predicted_str)
            amp.set_vals_smart(predicted)
        else:
            if instr_configs.mode[0] == "ACC":
                amp.set_curr(chan=instr_configs.channel, curr=instr_configs.current)
            elif instr_configs.mode[0] == "ALC":
                amp.set_power(chan=instr_configs.channel, power=instr_configs.power)
    rm.close()



def main():
    parser = argparse.ArgumentParser(
        description="Remote setup the instrument", 
        formatter_class=CustomArgparseFormatter
    )
    parser.add_argument("--instr", type=str, metavar="", dest="instr", nargs=1, help=f'Instruments: {", ".join(INSTR_TYPES)}', required=True)
    parser.add_argument("-f", "--filepath", type=str, metavar="", dest="filepath", nargs=1, default=("./configs/instr_config.yaml",), help="Path to the configuration file.", required=False)

    args = parser.parse_args()

    configs = load_config(args.filepath[0])
    setup(args.instr[0], configs)



if __name__ == "__main__":
    main()