import time
from os.path import join
from os import makedirs

from tqdm import tqdm
import pandas as pd
from pyvisa import ResourceManager

from pyoctal.instruments import AgilentE3640A, Agilent8163B
from pyoctal.utils.file_operations import export_to_csv

def run_one_source(rm: ResourceManager, pm_config: dict, mm_config: dict, folder: str):
    """ Run only with instrument. Require one voltage source """
    pm = AgilentE3640A(addr=pm_config["addr"], rm=rm)
    mm = Agilent8163B(addr=mm_config["addr"], rm=rm)

    for volt in tqdm(range(pm_config["start"], pm_config["stop"]+pm_config["step"], pm_config["step"])):

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
        
        export_to_csv(data=pd.DataFrame({"Wavelengths [m]": wavelengths, "Power [W]": powers}), filename=join(folder, f"{volt}.csv"))
    
    pm.set_volt(0)
    pm.set_output_state(0)




def main():
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

    folder = "data"
    makedirs(folder, exist_ok=True)
    rm = ResourceManager()

    run_one_source(rm, pm_config, mm_config, folder)

if __name__ == "__main__":
    main()