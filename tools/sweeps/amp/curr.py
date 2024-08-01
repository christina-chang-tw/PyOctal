"""
curr.py
=======
This script is used to sweep the current of an amplifier 
and measure the wavelength v.s. loss at different current levels.
The data will be saved in the specified folder alongisde the OMR files.
If prediction is specified, the script will also train a linear regression model.

To run this script:
    python -m tools.sweeps.amp.curr
"""
from pathlib import Path
from os import makedirs
import pickle

from tqdm import tqdm
import pandas as pd
import numpy as np
from pyvisa import ResourceManager

from sklearn.linear_model import LinearRegression

from pyoctal.instruments import FiberlabsAMP, KeysightILME
from pyoctal.instruments.keysightPAS import export_to_omr

def linear_regression(data: np.array):
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

    return model



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
    df = pd.read_csv(fpath, encoding='utf-8')
    output_curr = model.predict(wavelength, loss)

    # perform true value and set value mapping
    row = df.iloc[df[:,1] == output_curr]
    predicted = df.iloc[row, 0]

    return predicted


def run_curr(rm: ResourceManager, amp_config: dict,
             folder: Path, ilme_config: Path=None, prediction: bool=False):
    """
    Obtain wavelength v.s. loss at different current levels.

    You only need to set the min and max current that you want to set
    and the program will automatically set the driving current of each
    channel for you starting from the smallest channel.
    """
    currents = np.linspace(amp_config["start"], amp_config["stop"], amp_config["step"])

    amp = FiberlabsAMP(addr=amp_config["addr"], rm=rm)
    amp.set_ld_mode(chan=1, mode=amp_config.get("mode"))
    amp.set_all_curr(curr=0)
    amp.set_output_state(state=1)

    with KeysightILME(config_path=ilme_config) as ilme:
        # initialise a 2d loss array for model training
        if prediction:
            loss_2d_arr = np.zeros(shape=(ilme.get_dpts(), len(currents)))

        for j, curr in tqdm(enumerate(currents), desc="Currents", total=len(currents)):
            amp.set_curr_smart(mode=amp_config.get("mode"), val=curr)
            ilme.start_meas()
            wavelength, loss, omr_data = ilme.get_result()

            if prediction:
                loss_2d_arr[:,j] = loss

            pd.DataFrame(
                {"Wavelength": wavelength, "Loss [dB]": loss}
            ).to_csv(folder / f"{curr}A.csv", index=False)
            export_to_omr(omr_data, filename=folder / f"{curr}A.omr")

    if prediction:
        dpts = []
        for i, curr in enumerate(currents):
            for j, wlength in enumerate(wavelength):
                dpts.append((curr, wlength, loss_2d_arr[i,j]))
        dpts = np.array(dpts)
        # Save the data for developing model in the future.
        np.save(folder / "model_data.npy", dpts)
        model = linear_regression(dpts)
        # save the model to a .pkl file for future usage
        with open(folder / "model.pkl", "wb") as file:
            pickle.dump(model, file)

    amp.set_output_state(state=0)


def main():
    """ Entry point."""
    rm = ResourceManager()
    amp_config = {
        "addr": "GPIB0::1::INSTR",
        "start": 0, #[mA] or [mW]
        "stop": 100, #[mA] or [mW]
        "step": 10, # [mA] or [mW]
        "mode": "ACC", # ACC or ALC
    }
    folder = Path("data")
    makedirs(folder, exist_ok=True)

    run_curr(rm, amp_config, folder, prediction=True)

if __name__ == "__main__":
    main()
