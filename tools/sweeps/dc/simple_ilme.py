"""
Perform a basic sweep with one DC source and use
ILME to obtain the spectrums at different DC bias voltages.
"""
from os import makedirs
from pathlib import Path

import numpy as np
from pyvisa import ResourceManager
from tqdm import tqdm

from pyoctal.instruments import AgilentE3640A, KeysightILME
from pyoctal.instruments.keysightPAS import export_to_omr

def run_ilme(rm: ResourceManager, pm_config: dict, folder: Path, ilme_config: Path=None):
    """ Run with ILME engine """
    voltages = np.arange(pm_config["start"], pm_config["stop"]+pm_config["step"], pm_config["step"])

    pm = AgilentE3640A(addr=pm_config["addr"], rm=rm)
    pm.set_output_state(1)

    with KeysightILME(config_path=ilme_config) as ilme:
        for volt in tqdm(voltages, desc="Sweeping voltages"):
            pm.set_params(volt, 0.1)
            pm.wait_until_stable()

            ilme.start_meas()
            _, _, omr_data = ilme.get_result()

            export_to_omr(omr_data, folder / f"heater_{volt}V.omr")

    pm.set_volt(0)

def main():
    """ Entry point."""
    pm_config = {
        "addr": "GPIB0::6::INSTR",
        "start": 0, # [V]
        "stop": 0, # [V]
        "step": 1, # [V]
    }

    folder = r"C:\Users\Lab2052\Desktop\Users\Christina\2024-5-07\s4_2_ramzi_ring_g200\simple_ilme4"

    # remove the directory
    makedirs(folder, exist_ok=True)
    rm = ResourceManager()

    run_ilme(rm, pm_config, folder)

if __name__ == "__main__":
    main()
