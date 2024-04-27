import time
from os.path import join
from os import makedirs

from tqdm import tqdm
import pandas as pd
import numpy as np
from pyvisa import ResourceManager

from pyoctal.instruments import (
    Keithley6487,
    AgilentE3640A,
    Keithley2400
)

from pyoctal.utils.file_operations import export_to_csv

def run_6487(rm: ResourceManager, vs_config: dict):
    vs = Keithley6487(addr=vs_config["addr"], rm=rm)

    vs.set_laser_volt(0)
    vs.set_laser_state(1) # turn the laser on
    
    voltages = np.linspace(vs_config["start"], vs_config["stop"] + vs_config["step"], vs_config["step"])

    currents = []

    for volt in tqdm(voltages):
        vs.set_laser_volt(volt)
        
        # make sure that the voltage is stable
        while abs(vs.get_laser_volt() - volt) > 0.001:
            time.sleep(0.1)

        currents.append(vs.meas_curr()) # measure current and append

    vs.set_laser_volt(0)
    vs.set_laser_state(0) # turn the laser off

    return pd.DataFrame({"Voltage [V]": voltages, "Current [A]": currents})


def run_E3640A(rm: ResourceManager, pm_config: dict):
    pm = AgilentE3640A(addr=pm_config["addr"], rm=rm)

    pm.set_volt(0)
    pm.set_output_state(1) # turn the output on

    voltages = np.linspace(pm_config["start"], pm_config["stop"] + pm_config["step"], pm_config["step"])

    currents = []

    for volt in tqdm(voltages):
        pm.set_volt(volt)
        
        pm.wait_until_stable()

        currents.append(pm.get_curr())
    
    pm.set_volt(0)
    pm.set_output_state(0) # turn laser off
    return pd.DataFrame({"Voltage [V]": voltages, "Current [A]": currents})


def run_2400(rm: ResourceManager, smu_config: dict):
    smu = Keithley2400(addr=smu_config["addr"], rm=rm)
    smu.set_laser_volt(0)
    smu.set_laser_state(1) # turn the laser on

    voltages = np.linspace(smu_config["start"], smu_config["stop"] + smu_config["step"], smu_config["step"])

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

    return df, pd.DataFrame({"Voltage [V]": voltages, "Current [A]": currents})


def main():
    rm = ResourceManager()
    folder = "data"
    makedirs(folder, exist_ok=True)

    vs_config = {
        "addr": "GPIB0::1::INSTR",
        "start": 0, # [V]
        "stop": 2, # [V]
        "step": 0.01, # [V]
    }

    pm_config = {
        "addr": "GPIB0::2::INSTR",
        "start": 0, # [V]
        "stop": 2, # [V]
        "step": 0.01, # [V]
    }

    smu_config = {
        "addr": "GPIB0::3::INSTR",
        "start": 0, # [V]
        "stop": 2, # [V]
        "step": 0.01, # [V]
    }

    df = run_6487(rm, vs_config)
    export_to_csv(data=df, filename=join(folder, "6487.csv"))

    df = run_E3640A(rm, pm_config)
    export_to_csv(data=df, filename=join(folder, "E3640A.csv"))

    df, df2 = run_2400(rm, smu_config)
    export_to_csv(data=df, filename=join(folder, "2400.csv"))
    export_to_csv(data=df2, filename=join(folder, "2400_currents.csv"))

if __name__ == "__main__":
    main()