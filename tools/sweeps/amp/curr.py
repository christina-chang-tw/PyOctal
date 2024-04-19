from os.path import join

from tqdm import tqdm
import pandas as pd
import numpy as np
import pickle
from pyvisa import ResourceManager

from sklearn.linear_model import LinearRegression

from pyoctal.utils.file_operations import export_to_excel, export_to_csv
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


def run_curr(rm: ResourceManager, amp_config: dict, folder: str, prediction: bool=False): 
    """
    Obtain wavelength v.s. loss at different current levels.

    You only need to set the min and max current that you want to set
    and the program will automatically set the driving current of each
    channel for you starting from the smallest channel.
    """

    amp = FiberlabsAMP(addr=amp_config["addr"], rm=rm)
    ilme = KeysightILME()
    ilme.activate()

    currents = np.linspace(amp_config["start"], amp_config["stop"], amp_config["step"])

    # initialise a 2d loss array for model training
    if prediction:
        loss_2d_arr = np.zeros(shape=(ilme.get_dpts(), len(currents)))

    # make sure to set channel 1 to ACC mode
    amp.set_ld_mode(chan=1, mode=amp_config.get("mode"))
    amp.set_all_curr(curr=0)
    amp.set_output_state(state=1)

    for j, curr in tqdm(enumerate(currents), desc="Currents", total=len(currents)):
        amp.set_curr_smart(mode=amp_config.get("mode"), val=curr)
        ilme.start_meas()
        wavelength, loss, omr_data = ilme.get_result()

        if prediction:
            loss_2d_arr[:,j] = loss

        export_to_csv(pd.DataFrame({"Wavelength": wavelength, "Loss [dB]": loss}), sheet_names="data", folder=folder, fname=f"{curr}A.xlsx")
        export_to_omr(omr_data, join(folder, f"{curr}A.omr"))

    if prediction:
        dpts = []
        for i, curr in enumerate(currents):
            for j, wlength in enumerate(wavelength):
                dpts.append((curr, wlength, loss_2d_arr[i,j]))
        dpts = np.array(dpts)
        # Save the data for developing model in the future.
        np.save(f"{folder}/model_data.npy", dpts)
        model = linear_regression(dpts)
        # save the model to a .pkl file for future usage
        with open(f"{folder}/model.pkl", "wb") as file:
            pickle.dump(model, file)

    amp.set_output_state(state=0)


def main():
    rm = ResourceManager()
    amp_config = {
        "addr": "GPIB0::1::INSTR",
        "start": 0, #[mA] or [mW]
        "stop": 100, #[mA] or [mW]
        "step": 10, # [mA] or [mW]
        "mode": "ACC", # ACC or ALC
    }
    folder = "data"
    run_curr(rm, amp_config, folder, prediction=True)

if __name__ == "__main__":
    main()