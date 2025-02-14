"""
simply_dc.py
============
This script is used to perform a simple DC sweep with one voltage source and one power meter.
You sweep the voltage source and then measure the optical output power at a specified wavelength.

To run this script:
python -m tools.sweeps.dc.simple_dc
"""
from os import makedirs

import numpy as np
from tqdm import tqdm
import pandas as pd
from pyvisa import ResourceManager

from pyoctal.instruments import AgilentE3640A, Agilent8164B
from pyoctal.utils.file_operations import export_to_excel


def run(rm: ResourceManager, pm_config: dict, pm2_config: dict, mm_config: dict, filename: str):
    """
    Run the DC sweep with power in linear scale.
    
    Parameters
    ----------
    rm: ResourceManager
        Pyvisa resource manager
    pm_config: dict
        Power meter configuration
    mm_config: dict
        Laser/detector source configuration
    filename: Path
        The filename to save the data to
    """
    pm = AgilentE3640A(rm=rm)
    pm.connect(addr=pm_config["addr"])
    pm2 = AgilentE3640A(rm=rm)
    pm2.connect(addr=pm2_config["addr"])
    mm = Agilent8164B(rm=rm)
    mm.connect(addr=mm_config["addr"])

    currents = []
    powers = []
    opowers = []
    detected_voltages = []

    # power in linear scale
    ideal_powers = np.linspace(pm_config["start"]**2, pm_config["stop"]**2, num=pm_config["npts"])
    voltages = np.sqrt(ideal_powers)

    mm.setup(reset=0, wavelength=mm_config["wavelength"], power=mm_config["power"], period=mm_config["period"])
    pm2.set_params(pm2_config["v"], 0.5)
    pm2.set_output_state(1)
    
    # check if the limits are set correctly
    if pm.get_params()[0] < pm_config["stop"]:
        pm.set_params(pm_config["stop"], 0.5)

    # turn on the power meter if it is not already on
    
    
    pm.set_output_state(1)

    for volt in tqdm(voltages, desc="DC Sweep - linear power"):
        pm.set_volt(volt)

        pm.wait_until_stable()
        
        # wavelength = mm.find_resonance()
        # mm.set_wavelength(wavelength)
        volt = pm.get_volt()
        curr = pm.get_curr()
        detected_voltages.append(volt)
        currents.append(curr) # get the current value
        powers.append(volt*curr)
        opowers.append(mm.get_detect_pow())
        
    pd.DataFrame({"Voltage [V]": voltages, "Detected Voltage [V]": detected_voltages, "Current [A]": currents, "Electrical Power [W]": powers, "Optical power [W]": opowers}).to_csv(filename, index=False)
    pm.set_volt(0)
    rm.close()


def main():
    """ Entry point."""
    # power meter
    pm2_config = {
        "addr": "GPIB0::5::INSTR",
        "v": 0.5
    }

    pm_config = {
        "addr": "GPIB0::6::INSTR",
        "start": 0, # [V]
        "stop": 2.1, # [V]
        "npts": 121,
    }

    # laser/detector source
    mm_config = {
        "addr": "GPIB0::20::INSTR",
        "wavelength": 1547, # [nm]
        "power": 10, # [dBm]
        "period": 0.1, # [s]
    }
    filename = f"{pm2_config['v']}v_g200_max_2.csv"


    folder =  r"C:\Users\Lab2052\Desktop\Users\Christina\2024-6-10\ramzi_g200"
    # check that the directory exists first, else create it.
    makedirs(filename.parent, exist_ok=True)
    rm = ResourceManager()

    # sweep power in linear scale by specifying voltages and number of points
    run(rm, pm_config, pm2_config, mm_config, join(folder, filename))

if __name__ == "__main__":
    main()
