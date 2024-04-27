"""
simply_dc.py
============
This script is used to perform a simple DC sweep with one voltage source and one power meter.
You sweep the voltage source and then measure the optical output power at a specified wavelength.

To run this script:
python -m tools.sweeps.dc.simple_dc
"""

import time
from os.path import dirname
from os import makedirs
import numpy as np

from tqdm import tqdm
import pandas as pd
from pyvisa import ResourceManager

from pyoctal.instruments import AgilentE3640A, Agilent8163B
from pyoctal.utils.file_operations import export_to_csv


def run(rm: ResourceManager, pm_config: dict, mm_config: dict, filename: str):
    """ Run only with instrument. Require one voltage source """
    pm = AgilentE3640A(addr=pm_config["addr"], rm=rm)
    mm = Agilent8163B(addr=mm_config["addr"], rm=rm)


    currents = []
    opowers = []
    voltages = np.arange(pm_config["start"], pm_config["stop"]+pm_config["step"], pm_config["step"])

    mm.setup(reset=0, wavelength=mm_config["wavelength"], power=mm_config["power"], period=mm_config["period"])
    
    # check if the limits are set correctly
    if pm.get_params()[0] < pm_config["stop"]:
        pm.set_params(pm_config["stop"], 0.1)

    # turn on the power meter if it is not already on
    if not pm.get_output_state():
        pm.set_output_state(1)

    for volt in tqdm(voltages, desc="DC Sweep"):

        pm.set_volt(volt)
        
        pm.wait_until_stable()

        currents.append(pm.get_curr()) # get the current value
        opowers.append(mm.get_detect_pow())
        
    export_to_csv(data=pd.DataFrame({"Voltage [V]": voltages, "Current [A]": currents, "Optical power [W]": opowers}), filename=filename)
    
    pm.set_volt(0)


def main():
    # power meter
    pm_config = {
        "addr": "GPIB0::4::INSTR",
        "start": 0, # [V]
        "stop": 5, # [V]
        "step": 1, # [V]
    }

    # laser/detector source
    mm_config = {
        "addr": "GPIB0::20::INSTR",
        "wavelength": 1550, # [nm]
        "power": 10, # [dBm]
        "period": 0.1, # [s]
    }

    filename = "./data.csv"

    # check that the directory exists first, else create it.
    makedirs(dirname(filename), exist_ok=True)
    rm = ResourceManager()

    run(rm, pm_config, mm_config, filename)

if __name__ == "__main__":
    main()