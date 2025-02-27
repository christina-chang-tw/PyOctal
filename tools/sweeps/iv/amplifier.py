from pathlib import Path
from typing import Dict

import pandas as pd
import numpy as np
from pyvisa import ResourceManager
from tqdm import tqdm

from pyoctal.instruments import (
    AmetekDSP7265,
    AgilentE3640A,
)


def run_DSP7265_one(rm: ResourceManager, amp_config: Dict,
                    pm_config: Dict, filename: Path):
    """
    Run with one power meter and one amplifier.

    Parameters
    ----------
    rm: ResourceManager
        Pyvisa resource manager
    amp_config: dict
        Amplifier configuration
    pm_config: dict
        Power meter configuration
    filename: Path
        The filename to save the data to
    """
    pm = AgilentE3640A(rm=rm)
    pm.connect(addr=pm_config["addr"])
    amp = AmetekDSP7265(rm=rm)
    amp.connect(addr=amp_config["addr"])

    pm.set_volt(0)
    pm.set_output_state(1)

    currents = []
    opowers = []
    voltages = np.linspace(
        pm_config["start"], pm_config["stop"] + pm_config["step"], pm_config["step"]
    )

    for volt in tqdm(voltages):
        pm.set_volt(volt)

        pm.wait_until_stable()

        currents.append(pm.get_curr())
        opowers.append(amp.get_mag())


    pm.set_volt(0)
    pm.set_output_state(0)
    amp.set_mag(0)

    pd.DataFrame({
        "Voltage [V]": voltages,
        "Current [A]": currents,
        "Optical Power [W]": opowers 
    }).to_csv(filename, index=False)
    rm.close()

def run_DSP7265_dual(rm: ResourceManager, amp_config: Dict,
                     pm1_config:Dict,pm2_config: Dict, filename: Path):
    """
    Run with two power meters and one amplifier.

    Parameters
    ----------
    rm: ResourceManager
        Pyvisa resource manager
    amp_config: dict
        Amplifier configuration
    pm1_config: dict
        Power meter 1 configuration
    pm2_config: dict
        Power meter 2 configuration
    filename: Path
        The filename to save the data to
    """
    pm1 = AgilentE3640A(rm=rm)
    pm1.connect(addr=pm1_config["addr"])
    pm2 = AgilentE3640A(rm=rm)
    pm2.connect(addr=pm2_config["addr"])
    amp = AmetekDSP7265(rm=rm)
    amp.connect(addr=amp_config["addr"])

    pm1.set_volt(0)
    pm1.set_output_state(1)
    pm2.set_volt(0)
    pm2.set_output_state(1)

    df = pd.DataFrame(
        columns=["Volt1 [V]", "Volt2 [V]", "Current1 [A]", "Current2 [A]", "Optical [W]"]
    )

    pm1_voltages = np.linspace(
        pm1_config["start"], pm1_config["stop"] + pm1_config["step"], pm1_config["step"]
    )

    pm2_voltages = np.linspace(
        pm2_config["start"], pm2_config["stop"] + pm2_config["step"], pm2_config["step"]
    )

    for volt1 in tqdm(pm1_voltages):

        pm1.set_volt(volt1)
        curr1 = pm1.get_curr()

        for volt2 in pm2_voltages:
            pm2.set_volt(volt2)

            pm2.wait_until_stable()

            curr2 = pm2.get_curr()
            opower = amp.get_mag()
            data = (volt1, volt2, curr1, curr2, opower)
            df.loc[len(df)] = data

    pm1.set_volt(0)
    pm1.set_output_state(0)
    pm2.set_volt(0)
    pm2.set_output_state(0)
    amp.set_mag(0)

    df.to_csv(filename, index=False)
    rm.close()


def main():
    """ Entry point."""
    rm = ResourceManager()
    amp_config = {
        "addr": "GPIB0::6::INSTR",
    }
    pm1_config = {
        "addr": "GPIB0::10::INSTR",
        "start": 0, # [V]
        "stop": 1, # [V]
        "step": 0.1, # [V]
    }
    pm2_config = {
        "addr": "GPIB0::11::INSTR",
        "start": 0, # [V]
        "stop": 1, # [V]
        "step": 0.1, # [V]
    }

    filename = "a.csv"
    run_DSP7265_dual(rm, amp_config, pm1_config, pm2_config, filename)


if __name__ == "__main__":
    main()
