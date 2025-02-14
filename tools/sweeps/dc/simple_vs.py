from os import makedirs
from pathlib import Path

from tqdm import tqdm
import pandas as pd
from pyvisa import ResourceManager

from pyoctal.instruments import AgilentE3640A, Agilent8163B

def run_one_source(rm: ResourceManager, pm_config: dict, mm_config: dict, folder: Path):
    """ Run only with instrument. Require one voltage source """
    pm = AgilentE3640A(rm=rm)
    pm.connect(addr=pm_config["addr"])
    mm = Agilent8163B(rm=rm)
    mm.connect(addr=mm_config["addr"])

    voltages = range(pm_config["start"], pm_config["stop"]+pm_config["step"], pm_config["step"])

    for volt in tqdm(voltages):

        pm.set_volt(volt)

        pm.wait_until_stable()

        # get the loss v.s. wavelength
        wavelengths, powers = mm.run_laser_sweep_auto(
            power=mm_config["power"],
            start=mm_config["start"],
            stop=mm_config["stop"],
            step=mm_config["step"],
            speed=mm_config["speed"],
            cycles=mm_config["cycles"],
            )

        pd.DataFrame({
            "Wavelengths [m]": wavelengths,
            "Power [W]": powers
        }).to_csv(folder / f"{volt}V.csv", index=False)

    pm.set_volt(0)
    pm.set_output_state(0)

def main():
    """ Entry point."""
    pm_config = {
        "addr": "GPIB0::5::INSTR",
        "start": 0, # [V]
        "stop": 5, # [V]
        "step": 1, # [V]
    }

    mm_config = {
        "addr": "GPIB0::6::INSTR",
        "power": 10, # [dBm]
        "start": 1530, # [nm]
        "stop": 1570, # [nm]
        "step": 5, # [nm]
        "speed": 5, # nm/s
        "cycles": 1,
    }

    folder = Path("data")
    makedirs(folder, exist_ok=True)
    rm = ResourceManager()

    run_one_source(rm, pm_config, mm_config, folder)

if __name__ == "__main__":
    main()
