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
)

def run(rm: ResourceManager, vs_config: dict, filename: Path):
    vs = Keithley6487(rm=rm)
    vs.connect(addr=vs_config["addr"])

    vs.set_volt(vs_config["voltage"])
    vs.set_output_state(1)

    voltages = []
    currents = []
    resistances = []

    try:
        while True:
            voltage = vs.meas_volt()
            current = vs.meas_curr()
            voltages.append(voltage)
            currents.append(current) # measure current and append
            resistances.append(voltage/current)

            df = pd.DataFrame({
                "Voltage (V)": voltages,
                "Current (A)": currents,
                "Resistance (Ohm)": resistances
            })
            df.to_csv(filename, index=False)
            time.sleep(vs_config["interval"] * 60) # measured in seconds
    finally:
        df = pd.DataFrame({
            "Voltage (V)": voltages,
            "Current (A)": currents,
            "Resistance (Ohm)": resistances
        })
        df.to_csv(filename, index=False)
        vs.set_volt(0)
        vs.set_output_state(0) # turn the laser off
        rm.close()


def main():
    """ Entry point."""
    rm = ResourceManager()
    path = Path(r"data")

    if path.is_dir():
        makedirs(path, exist_ok=True)
    else:
        makedirs(path.parent, exist_ok=True)

    vs_config = {
        "addr": "GPIB0::1::INSTR",
        "voltage": 0, # [V]
        "interval": 5 # minutes
    }

    run(rm, pm_config, path)

if __name__ == "__main__":
    main()
