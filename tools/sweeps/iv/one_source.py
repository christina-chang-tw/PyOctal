import time
from os import makedirs
from pathlib import Path
from typing import Dict

from tqdm import tqdm
import pandas as pd
import numpy as np
from pyvisa import ResourceManager

from pyoctal.instruments import (
    Keithley6487,
    AgilentE3640A,
    Keithley2400
)

def run_6487(rm: ResourceManager, vs_config: dict, filename: Path):
    vs = Keithley6487(rm=rm)
    vs.connect(addr=vs_config["addr"])

    vs.set_laser_volt(0)
    vs.set_laser_state(1) # turn the laser on

    voltages = np.linspace(vs_config["start"],
                           vs_config["stop"] + vs_config["step"], vs_config["step"])

    currents = []

    for volt in tqdm(voltages):
        vs.set_laser_volt(volt)

        # make sure that the voltage is stable
        while abs(vs.get_laser_volt() - volt) > 0.001:
            time.sleep(0.1)

        currents.append(vs.meas_curr()) # measure current and append

    vs.set_laser_volt(0)
    vs.set_laser_state(0) # turn the laser off

    pd.DataFrame({"Voltage [V]": voltages, "Current [A]": currents}).to_csv(filename)


def run_E3640A(rm: ResourceManager, pm_config: Dict, filename: Path):
    """
    Measure current using Agilent E3640A.

    Parameters
    ----------
    rm: ResourceManager
        Pyvisa resource manager
    pm_config: dict
        Configuration for Keithley 6487
    filename: Path
        file to save the data
    """
    pm = AgilentE3640A(rm=rm)
    pm.connect(addr=pm_config["addr"])

    pm.set_volt(0)
    pm.set_output_state(1) # turn the output on

    voltages = np.linspace(pm_config["start"],
                           pm_config["stop"] + pm_config["step"], pm_config["step"])

    currents = []
    pm.set_params(pm_config["stop"], 0.1)

    for volt in tqdm(voltages):
        pm.set_volt(volt)

        pm.wait_until_stable()

        currents.append(pm.get_curr())

    pm.set_volt(0)
    pm.set_output_state(0) # turn laser off

    pd.DataFrame({"Voltage [V]": voltages, "Current [A]": currents}).to_csv(filename)

def run_2400(rm: ResourceManager, smu_config: Dict, folder: Path):
    """
    Measure current using Keithley 2400.

    Parameters
    ----------
    rm: ResourceManager
        Pyvisa resource manager
    pm_config: dict
        Configuration for Keithley 6487
    folder: Path
        The folde to save the files
    """
    smu = Keithley2400(rm=rm)
    smu.connect(addr=smu_config["addr"])
    smu.set_laser_volt(0)
    smu.set_laser_state(1) # turn the laser on

    voltages = np.linspace(smu_config["start"],
                           smu_config["stop"] + smu_config["step"], smu_config["step"])

    df = pd.DataFrame()
    currents = []

    for volt in tqdm(voltages):
        smu.set_laser_volt(volt)

        while abs(smu.get_laser_volt() - volt) > 0.001:
            time.sleep(0.1)

        df[f"{volt}V"], curr = smu.meas_curr_buf(volt, 200, 1)
        currents.append(curr)

    smu.set_laser_volt(0)
    smu.set_laser_state(0) # turn the laser off

    df.to_csv(folder / "2400.csv")
    pd.DataFrame({
        "Voltage [V]": voltages,
        "Current [A]": currents
    }).to_csv(folder / "2400_currents.csv")

def main():
    """ Entry point."""
    rm = ResourceManager()
    path = Path(r"data")

    if path.is_dir():
        makedirs(path, exist_ok=True)
    else:
        makedirs(path.parent, exist_ok=True)

    # vs_config = {
    #     "addr": "GPIB0::1::INSTR",
    #     "start": 0, # [V]
    #     "stop": 2, # [V]
    #     "step": 0.01, # [V]
    # }

    pm_config = {
        "addr": "GPIB0::6::INSTR",
        "start": 0, # [V]
        "stop": 10, # [V]
        "step": 0.01, # [V]
    }

    # smu_config = {
    #     "addr": "GPIB0::3::INSTR",
    #     "start": 0, # [V]
    #     "stop": 2, # [V]
    #     "step": 0.01, # [V]
    # }

    run_E3640A(rm, pm_config, path)

if __name__ == "__main__":
    main()
