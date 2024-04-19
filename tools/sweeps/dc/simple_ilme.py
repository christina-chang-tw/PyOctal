"""
Perform a basic sweep with one DC source and use
ILME to obtain the spectrums at different DC bias voltages.
"""
from os import makedirs
from os.path import join
import time

import numpy as np
from pyvisa import ResourceManager
from tqdm import tqdm
import pandas as pd

from pyoctal.instruments import AgilentE3640A, KeysightILME
from pyoctal.utils.file_operations import export_to_csv
from pyoctal.instruments.keysightPAS import export_to_omr

def run_ilme(rm: ResourceManager, pm_config: dict, folder: str):
    """ Run with ILME engine """

    pm = AgilentE3640A(addr=pm_config["addr"], rm=rm)
    ilme = KeysightILME()
    ilme.activate()
    currents = []
    df = pd.DataFrame()

    for volt in tqdm(np.arange(pm_config["start"], pm_config["stop"]+pm_config["step"], pm_config["step"])):
        pm.set_volt(volt)
        time.sleep(0.1)
        currents.append(pm.get_curr()) # get the current value

        ilme.start_meas()
        wavelength, loss, omr_data = ilme.get_result()
        df["Wavelength"] = wavelength
        df["Loss [dB]"] = loss

        export_to_csv(data=df, filename=join(folder, "csv", f"{volt}V.csv"))
        export_to_omr(omr_data, join(folder, "omr", f"{volt}V.omr"))

    pm.set_volt(0)

def main():
    pm_config = {
        "addr": "GPIB0::5::INSTR",
        "start": 0, # [V]
        "stop": 5, # [V]
        "step": 1, # [V]
    }

    folder = "data"
    makedirs(folder, exist_ok=True)
    rm = ResourceManager()

    run_ilme(rm, pm_config, folder)

if __name__ == "__main__":
    main()