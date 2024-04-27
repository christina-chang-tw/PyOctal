"""
This script is used to sweep the voltage of a single source and measure the power of the output of a MZI.
"""
from os.path import join
from os import makedirs

from tqdm import tqdm
import pandas as pd
import numpy as np
import sys
from pyvisa import ResourceManager

from pyoctal.instruments import AgilentE3640A, Agilent8164B
from pyoctal.utils.file_operations import export_to_csv

def run_one_source_mzi(rm: ResourceManager, pm_config: dict, mm_config: dict):
    """ Run only with instrument. Require one voltage source """
    pm = AgilentE3640A(addr=pm_config["addr"], rm=rm)
    mm = Agilent8164B(addr=mm_config["addr"], rm=rm)
    avg = 3

    powers = []
    currents = []
    voltages = np.arange(pm_config["start"], pm_config["stop"]+pm_config["step"], pm_config["step"])

    pm.set_output_state(1)
    pm.set_params(pm_config["stop"], 0.5)

    for volt in tqdm(voltages):

        pm.set_volt(volt)
        power = 0
        
        # wait until the current is stable
        pm.wait_until_stable()

        for _ in range(avg):
            power += mm.get_detect_pow()
        powers.append(power/avg)
        currents.append(pm.get_curr())

    pm.set_volt(0)
    pm.set_output_state(0)

    return voltages, powers, currents


def main():
    pm_config = {
        "addr": "GPIB0::5::INSTR",
        "start": 0,
        "stop": 5,
        "step": 1,
    }

    mm_config = {
        "addr": "GPIB0::6::INSTR",
    }

    folder = "data"
    makedirs(folder, exist_ok=True)
    rm = ResourceManager()

    voltages, powers, currents = run_one_source_mzi(rm, pm_config, mm_config)

    df = pd.DataFrame()
    df["Voltage [V]"] = voltages
    df["Power [dBm]"] = powers
    df["Current [A]"] = currents

    export_to_csv(data=df, filename=join(folder, "data.csv"))


if __name__ == "__main__":
    main()