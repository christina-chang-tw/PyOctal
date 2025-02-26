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

    pm = AgilentE3640A(rm=rm)
    pm.connect(addr=pm_config["addr"])
    pm.set_output_state(1)
    
    ilme = KeysightILME()
    ilme.connect(config_path=ilme_config)

    for volt in tqdm(voltages, desc="Sweeping voltages"):
        pm.set_params(volt, 0.1)
        pm.wait_until_stable()

        ilme.start_meas()
        _, _, omr_data = ilme.get_result()

        export_to_omr(omr_data, folder / f"heater_{volt}V.omr")

    pm.set_volt(0)
    rm.close()

def main():
    """ Entry point."""
    pm_config = {
        "addr": "GPIB0::4::INSTR",
        "start": 0, # [V]
        "stop": 20, # [V]
        "step": 1, # [V]
    }

    folder = Path(r"Y:\Christina\ktn tests\KTN 2024 Nov\09.12.2024")

    # remove the directory
    makedirs(folder, exist_ok=True)
    rm = ResourceManager()

    run_ilme(rm, pm_config, folder)

if __name__ == "__main__":
    main()
