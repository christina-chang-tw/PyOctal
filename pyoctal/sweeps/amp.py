from tqdm import tqdm
import pandas as pd
import numpy as np
from typing import Union

from pyoctal.util.file_operations import export_to_excel, export_to_csv
from pyoctal.base import BaseSweeps
from pyoctal.instruments import FiberlabsAMP, KeysightILME

class AMPSweeps(BaseSweeps):
    """
    Amplifier Sweeps

    This sweeps through the voltage range and obtains the information
    about the insertion loss against wavelength 

    Parameters
    ----------
    ttype_configs: dict
        Test type specific configuration parameters
    instr_addrs: map
        All instrument addresses
    rm:
        Pyvisa resource manager
    folder: str
        Path to the folder
    fname: str
        Filename
    """

    def __init__(self, ttype_configs: dict, instr_addrs: dict, rm, folder: str, fname: str):
        super().__init__(instr_addrs=instr_addrs, rm=rm, folder=folder, fname=fname)
        self.mode = ttype_configs.mode
        self.start = ttype_configs.start
        self.stop = ttype_configs.stop
        self.step = ttype_configs.step
        self.channels = ttype_configs.channels


    def run_acc(self):
        self.instrment_check("amp", self._addrs.keys())

        amp = FiberlabsAMP(addr=self._addrs.amp, rm=self._rm)
        ilme = KeysightILME()
        ilme.activate()

        df = pd.DataFrame()
        currents = range(self.start, self.stop, self.step)
        additional_data = np.zeros(shape=(len(self.channels)*len(currents), 6))

        # package information:
        config_info = {
            "Wavelength start [nm]" : ilme.wavelength_start,
            "Wavelength stop [nm]"  : ilme.wavelength_stop,
            "Wavelength step [nm]"  : ilme.wavelength_step,
            "Sweep rate [nm/s]"     : ilme.sweep_rate,
            "Output power [dBm]"    : ilme.tls_power,
        }

        # print sweep information
        for key, val in config_info.items():
            print(f"{key:22} : {val}")

        amp.set_output_state(state=1)

        for i, chan in enumerate(self.channels):
            for j, curr in tqdm(enumerate(currents), desc=f"Channel {chan}"):
                amp.set_curr(chan=chan, curr=curr)
                amp.curr_wait_till_stabalise(chan=chan) # wait until it is stabalise

                # Additional information #####
                acc_curr = amp.get_curr(chan=chan)
                mon_ld = amp.get_mon_pump_ld(chan=chan)
                mon_temp = amp.get_mon_pump_temp(chan=chan)
                mon_ipower = amp.get_mon_input_power()
                mon_opower = amp.get_mon_output_power()
                additional_data[i*len(currents)+j] = (curr, acc_curr, mon_ld, mon_temp, mon_ipower, mon_opower)
                ##############################

                ilme.start_meas()
                xdata, ydata = ilme.get_result()
                print(len(xdata), len(ydata))
                df["Wavelength"] = xdata
                df["Loss [dB]"] = ydata

                export_to_excel(data=pd.DataFrame(config_info.items()), sheet_names="config", folder=f"{self.folder}/CH{chan}", fname=f"{curr}A.xlsx")
                export_to_excel(data=df, sheet_names="data", folder=f"{self.folder}/CH{chan}", fname=f"{curr}A.xlsx")

        amp.set_output_state(state=0)

