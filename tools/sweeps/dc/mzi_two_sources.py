from os import makedirs
from pathlib import Path
import time

import numpy as np
from pyvisa import ResourceManager
from tqdm import tqdm
import pandas as pd

from pyoctal.instruments import AgilentE3640A, Agilent8164B

def run_ring_assisted_mzi(rm: ResourceManager, rpm_config: dict,
                          hpm_config: dict, mm_config: dict, folder: Path):
    """ 
    Try to see how the output power of a specific wavelength
    changes with the voltage of the MZI and the ring.
    """
    avg = 3

    heater_pm = AgilentE3640A(addr=hpm_config.pop["addr"], rm=rm)
    ring_pm = AgilentE3640A(addr=rpm_config.pop["addr"], rm=rm)
    mm = Agilent8164B(addr=mm_config.pop["addr"], rm=rm)
    mm.setup(**mm_config)

    heater_voltages = np.arange(
        hpm_config["start"], hpm_config["stop"] + hpm_config["step"], hpm_config["step"]
    )
    ring_voltages = np.arange(
        rpm_config["start"], rpm_config["stop"] + rpm_config["step"], rpm_config["step"]
    )

    heater_pm.set_output_state(1)
    heater_pm.set_params(hpm_config["stop"], 0.5)
    ring_pm.set_output_state(1)
    ring_pm.set_params(rpm_config["stop"], 0.1)

    max_min_voltages = np.zeros(shape=(len(ring_voltages), 3))
    for i, ring_v in tqdm(enumerate(ring_voltages), total=len(ring_voltages)):
        powers = []
        currents = []

        ring_pm.set_volt(ring_v)

        for volt in heater_voltages:

            heater_pm.set_volt(volt)

            # wait until the current is stable
            heater_pm.wait_until_stable()

            time.sleep(0.2)
            power = 0
            for _ in range(avg):
                power += mm.get_detect_pow()
            powers.append(power/avg)
            currents.append(heater_pm.get_curr())

        pd.DataFrame({
            "Voltage [V]": heater_voltages,
            "Current [A]":currents,
            "Electrical Power [W]": heater_voltages*currents,
            "Power [W]": powers}
        ).to_csv(filename=folder / f"ring{ring_v}.csv", index=False)

        max_v = heater_voltages[np.argmax(powers)]
        min_v = heater_voltages[np.argmin(powers)]
        max_min_voltages[i] = [ring_v, max_v, min_v]

    heater_pm.set_volt(0)
    heater_pm.set_output_state(0)
    ring_pm.set_volt(0)
    ring_pm.set_output_state(0)

def main():
    """ Entry point."""
    rm = ResourceManager()
    folder = Path(r"C:\Users\Lab2052\Desktop\Users\Christina\2024-5-06\s4_2_ramzi_ring_g200\min")

    rpm_config = {
        "addr": "GPIB0::5::INSTR",
        "start": 0, # [V]
        "stop": 3, # [V]
        "step": 0.5, # [V]
    }
    hpm_config = {
        "addr": "GPIB0::6::INSTR",
        "start": 0, # [V]
        "stop": 2.2, # [V]
        "step": 0.02, # [V]
    }
    mm_config = {
        "addr": "GPIB0::20::INSTR",
        "wavelength": 1551.85 # [nm]
    }

    makedirs(folder.parent, exist_ok=True)

    run_ring_assisted_mzi(rm, rpm_config=rpm_config, hpm_config=hpm_config, mm_config=mm_config, folder=folder)

if __name__ == "__main__":
    main()
