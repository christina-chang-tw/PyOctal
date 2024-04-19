import time
from os.path import join
from os import makedirs

import pandas as pd
import numpy as np
from pyvisa import ResourceManager
from tqdm import tqdm

from pyoctal.instruments import (
    AmetekDSP7265,
    AgilentE3640A,
)

from pyoctal.utils.file_operations import export_to_csv


def run_DSP7265_one(rm: ResourceManager, amp_config: dict, pm_config: dict):
    pm = AgilentE3640A(addr=pm_config["addr"], rm=rm)
    amp = AmetekDSP7265(addr=amp_config["addr"], rm=rm)

    pm.set_volt(0)
    pm.set_output_state(1)

    currents = []
    opowers = []
    voltages = np.linspace(pm_config["start"], pm_config["stop"] + pm_config["step"], pm_config["step"])

    for volt in tqdm(voltages):
        pm.set_volt(volt)
        
        while abs(pm.get_volt() - volt) > 0.001:
            time.sleep(0.1)

        currents.append(pm.get_curr())
        opowers.append(amp.get_mag())


    pm.set_volt(0)
    pm.set_output_state(0)
    amp.set_mag(0)

    return pd.DataFrame({"Voltage [V]": voltages, "Current [A]": currents, "Optical Power [W]": opowers})

def run_DSP7265_dual(rm: ResourceManager, amp_config: dict, pm1_config: dict, pm2_config: dict):
    pm1 = AgilentE3640A(addr=pm1_config["addr"], rm=rm)
    pm2 = AgilentE3640A(addr=pm2_config["addr"], rm=rm)
    amp = AmetekDSP7265(addr=amp_config["addr"], rm=rm)

    pm1.set_volt(0)
    pm1.set_output_state(1)
    pm2.set_volt(0)
    pm2.set_output_state(1)

    df = pd.DataFrame(columns=["Volt1 [V]", "Volt2 [V]", "Current1 [A]", "Current2 [A]", "Optical [W]"])

    pm1_voltages = np.linspace(pm1_config["start"], pm1_config["stop"] + pm1_config["step"], pm1_config["step"])

    pm2_voltages = np.linspace(pm2_config["start"], pm2_config["stop"] + pm2_config["step"], pm2_config["step"])

    for volt1 in tqdm(pm1_voltages):

        pm1.set_volt(volt1)
        curr1 = pm1.get_curr()

        for volt2 in pm2_voltages:
            pm2.set_volt(volt2)

            while abs(pm2.get_volt() - volt2) > 0.001:
                time.sleep(0.1)

            curr2 = pm2.get_curr()
            opower = amp.get_mag()
            data = (volt1, volt2, curr1, curr2, opower)
            df.loc[len(df)] = data

    pm1.set_volt(0)
    pm1.set_output_state(0)
    pm2.set_volt(0)
    pm2.set_output_state(0)
    amp.set_mag(0)

    return df


def main():
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

    df = run_DSP7265_dual(rm, amp_config, pm1_config, pm2_config)
    makedirs("data", exist_ok=True)
    export_to_csv(df, "data/dual_pm.csv")


if __name__ == "__main__":
    main()
