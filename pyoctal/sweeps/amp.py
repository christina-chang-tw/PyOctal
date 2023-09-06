from tqdm import tqdm
import pandas as pd
import numpy as np
import math
from sklearn.linear_model import LinearRegression
import pickle
import logging

from pyoctal.util.formatter import Colours
from pyoctal.util.file_operations import export_to_excel, export_to_csv, get_dataframe_from_csv
from pyoctal.base import BaseSweeps
from pyoctal.instruments import FiberlabsAMP, KeysightILME

logger = logging.getLogger(__name__)

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
        self.prediction = ttype_configs.prediction
        self.mode = ttype_configs.mode
        self.start = ttype_configs.start
        self.stop = ttype_configs.stop
        self.step = ttype_configs.step
        
    @staticmethod
    def linear_regression(pkl_fpath: str, data: np.array):
        """ 
        Create a linear regression model.

        data: numpy.array
            data[0]: output currents/power
            data[1]: wavelength
            data[2]: loss
        """
        model = LinearRegression()
        indep_vars = np.column_stack((data[1], data[2]))
        model.fit(indep_vars, data[0])

        # save the model to a .pkl file for future usage
        with open(pkl_fpath, "wb") as file:
            pickle.dump(model, file)
        return model
    

    @staticmethod
    def predict(model, fpath: str, wavelength: float, loss: float):
        """ 
        Predict the required setting. 
        
        Parameters
        ----------
        model: 
            Machine learning model
        fpath: str
            Path to the file which contains the discrepancy between
            the user-defined current and the true output current.
        wavelength: float [nm]
        loss: float [dB]
        """
        # predict the output current

        # read in a file containing at these two columns with the first two being:
        # col0: set current/power (user sets this)
        # col1: output current/power (monitored by the instrument)
        df = get_dataframe_from_csv(fpath)
        output_curr = model.predict(wavelength, loss)

        # perform true value and set value mapping
        row = df.iloc[df[:,1] == output_curr]
        predicted = df.iloc[row, 0]

        return predicted


    def run_acc(self):
        self.instrment_check("amp", self._addrs.keys())

        amp = FiberlabsAMP(addr=self._addrs.amp, rm=self._rm)
        ilme = KeysightILME()
        ilme.activate()

        # package information:
        config_info = {
            "Wavelength start [nm]" : ilme.wavelength_start,
            "Wavelength stop [nm]"  : ilme.wavelength_stop,
            "Wavelength step [pm]"  : ilme.wavelength_step,
            "Sweep rate [nm/s]"     : ilme.sweep_rate,
            "Output power [dBm]"    : ilme.tls_power,
        }

        # print sweep information
        logger.info(Colours.underline + Colours.bold + Colours.italic + "ILME Configurations" + Colours.end)
        for key, val in config_info.items():
            print(f"{key:22} : {val}")

        currents = range(self.start, self.stop, self.step)
        
        extra_data_cols = ("Current [mA]", "Monitored Current [mA]", "Monitored Temperature [deg]")
        extra_data = np.zeros(shape=(len(currents), 3))

        # initialise a 2d loss array for model training
        if self.prediction:
            loss_2d_arr = np.zeros(shape=(ilme.get_dpts(), len(currents)))

        # make sure to set channel 1 to ACC mode
        amp.set_ld_mode(chan=1, mode=self.mode)
        amp.set_output_state(state=1)

        for j, curr in tqdm(enumerate(currents), desc="Currents", total=len(currents)):
            df = pd.DataFrame()
            chan = math.floor(curr/amp.chan_curr_max) + 1
            set_curr = curr % amp.chan_curr_max

            amp.set_curr(chan=chan, curr=set_curr)
            amp.wait_till_curr_is_stabalised(chan=chan) # wait until it is stabalise

            # Additional information #####
            mon_curr = sum(amp.get_mon_pump_curr()) # the output current is additive of the all channels' output
            mon_temp = amp.get_mon_pump_temp(chan=chan)
            extra_data[j] = (curr, mon_curr, mon_temp)
            ##############################

            ilme.start_meas()
            wavelength, loss = ilme.get_result()
            if self.prediction:
                loss_2d_arr[:,j] = loss
            
            df["Wavelength"] = wavelength
            df["Loss [dB]"] = loss
            fname = f"{curr}A.xlsx"
            export_to_excel(data=pd.DataFrame(config_info.items()), sheet_names="config", folder=self.folder, fname=fname)
            export_to_excel(data=df, sheet_names="data", folder=self.folder, fname=fname)

        if self.prediction:
            dpts = []
            for i, curr in enumerate(currents):
                for j, wlength in enumerate(wavelength):
                    dpts.append((curr, wlength, loss_2d_arr[i,j]))
            dpts = np.array(dpts)
            # Save the data for developing model in the future.
            np.save(f"{self.folder}/model_data.npy", dpts)
            _ = self.linear_regression(f"{self.folder}/model.pkl", dpts)
            

        export_to_csv(data=pd.DataFrame(extra_data, columns=extra_data_cols), folder=self.folder, fname="extra_data.csv")
        amp.set_output_state(state=0)

