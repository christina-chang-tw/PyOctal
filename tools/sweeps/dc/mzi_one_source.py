"""
This script is used to sweep the voltage of a single source
and measure the power of the output of a MZI.
"""
from os import makedirs
import time
from pathlib import Path

from tqdm import tqdm
import pandas as pd
import numpy as np
from pyvisa import ResourceManager

from pyoctal.instruments import AgilentE3640A, Agilent8164B

def run_one_source_mzi(rm: ResourceManager, pm_config: dict, mm_config: dict, filename: Path):
    """ Run only with instrument. Require one voltage source """
    pm = AgilentE3640A(addr=pm_config.pop["addr"], rm=rm)
    mm = Agilent8164B(addr=mm_config.pop["addr"], rm=rm)
    mm.setup(**mm_config)

    avg = 3

    powers = []
    currents = []
    voltages = np.arange(pm_config["start"], pm_config["stop"]+pm_config["step"], pm_config["step"])

    pm.set_output_state(1)
    pm.set_params(pm_config["stop"], 0.6)

    for volt in tqdm(voltages):

        pm.set_volt(volt)
        power = 0

        # wait until the current is stable
        pm.wait_until_stable()
        time.sleep(0.1)

        for _ in range(avg):
            power += mm.get_detect_pow()
        powers.append(power/avg)
        currents.append(pm.get_curr())

    pm.set_volt(0)
    pm.set_output_state(0)

    df = pd.DataFrame()
    df["Voltage [V]"] = voltages
    df["Current [A]"] = currents
    df["Electrical power [W]"] = df["Voltage [V]"]*df["Current [A]"]
    df["Power [W]"] = powers

    df.to_csv(filename, index=False)


def main():
    """ Entry point."""
    pm_config = {
        "addr": "GPIB0::6::INSTR",
        "start": 0,
        "stop": 3,
        "step": 0.025,
    }

    mm_config = {
        "addr": "GPIB0::20::INSTR",
        "wavelength": 1553.15
    }

    filename = Path(r"C:\Users\Lab2052\Desktop\Users\Christina \
                    \2024-5-07\s4_2_ramzi_ring_g200_3\ring3v_max_with_heater.csv")

    makedirs(filename.parent, exist_ok=True)
    rm = ResourceManager()

    run_one_source_mzi(rm, pm_config, mm_config, filename=filename)

    


if __name__ == "__main__":
    main()