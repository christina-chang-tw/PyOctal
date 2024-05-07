"""
Perform a basic sweep with one DC source and use
ILME to obtain the spectrums at different DC bias voltages.
"""
from os import makedirs
from os.path import join
from shutil import rmtree

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
    df = pd.DataFrame()
    pm.set_output_state(1)

    voltages = np.arange(pm_config["start"], pm_config["stop"]+pm_config["step"], pm_config["step"])

    for volt in tqdm(voltages, desc="Sweeping voltages"):
        pm.set_params(volt, 0.1)

        pm.wait_until_stable()

        ilme.start_meas()
        wavelength, loss, omr_data = ilme.get_result()
        df["Wavelength"] = wavelength
        df["Loss [dB]"] = loss

        export_to_csv(data=df, filename=join(folder, "csv", f"heater_{volt}V.csv"))
        export_to_omr(omr_data, join(folder, "omr", f"heater_{volt}V.omr"))

    pm.set_volt(0)

def main():
    pm_config = {
        "addr": "GPIB0::5::INSTR",
        "start": 0, # [V]
        "stop": 3, # [V]
        "step": 0.5, # [V]
    }

    folder = r"C:\Users\Lab2052\Desktop\Users\Christina\2024-5-07\s4_2_ramzi_ring_g200\simple_ilme4"
    # remove the directory
    rmtree(folder, ignore_errors=True)
    makedirs(folder, exist_ok=True)
    rm = ResourceManager()

    run_ilme(rm, pm_config, folder)

if __name__ == "__main__":
    main()