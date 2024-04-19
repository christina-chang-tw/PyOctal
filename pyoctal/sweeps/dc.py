import time
from os.path import join
from os import makedirs

import pandas as pd
from tqdm import tqdm
import numpy as np

from pyoctal.instruments import AgilentE3640A, Agilent8163B, KeysightILME, Agilent8164B
from pyoctal.utils.util import DictObj
from pyoctal.instruments.keysightPAS import export_to_omr
from pyoctal.instruments.base import BaseSweeps
from pyoctal.utils.file_operations import export_to_csv

class DCSweeps(BaseSweeps):
    """
    DC Sweeps

    This sweeps through the voltage range and obtains the information
    about the insertion loss against wavelength 

    Parameters
    ----------
    ttype_configs: dict
        Test type specific configuration parameters
    addrs: map
        All instrument addresses
    rm:
        Pyvisa resource manager
    folder: str
        Path to the folder
    fname: str
        Filename
    """
    def __init__(self, ttype_configs: dict, addrs: dict, rm, folder: str, fname: str):
        super().__init__(addrs=addrs, rm=rm, folder=folder, fname=fname)
        self.v_start = ttype_configs.v_start
        self.v_stop = ttype_configs.v_stop
        self.v_step = ttype_configs.v_step
        self.cycles = ttype_configs.cycles
        self.w_start = ttype_configs.lambda_start,
        self.w_stop = ttype_configs.lambda_stop,
        self.w_step = ttype_configs.lambda_step*pow(10, 3)
        self.w_speed = ttype_configs.lambda_speed
        self.power = ttype_configs.power
        self.omr_save = ttype_configs.omr_save
        self.currents = []
        self.df = pd.DataFrame()


    def run_ilme(self):
        """ Run with ILME engine """
        self.instrment_check("pm", self._addrs.keys())

        pm = AgilentE3640A(addr=self._addrs["pm"], rm=self._rm)
        ilme = KeysightILME()
        ilme.activate()

        for volt in tqdm(np.arange(self.v_start, self.v_stop+self.v_step, self.v_step)):
            pm.set_volt(volt)
            time.sleep(0.1)
            self.currents.append(pm.get_curr()) # get the current value

            ilme.start_meas()
            wavelength, loss, omr_data = ilme.get_result()
            self.df["Wavelength"] = wavelength
            self.df["Loss [dB]"] = loss

            export_to_csv(data=self.df, filename=join(self.folder, f"{volt}V.csv"))

            if self.omr_save:
                export_to_omr(omr_data, join(self.folder, f"{volt}V.omr"))

        pm.set_volt(0)


    def run_one_source(self):
        """ Run only with instrument. Require one voltage source """
        self.instrment_check(("pm", "mm"), self._addrs.keys())
        pm = AgilentE3640A(addr=self._addrs["pm"], rm=self._rm)
        mm = Agilent8163B(addr=self._addrs["mm"], rm=self._rm)

        for volt in tqdm(range(self.v_start, self.v_stop+self.v_step, self.v_step)):
            pm.set_volt(volt)
            time.sleep(0.1)
            self.currents.append(pm.get_curr()) # get the current value

            pm.set_volt(0)

            # get the loss v.s. wavelength
            self.df[f"{volt}V"] = mm.run_laser_sweep_auto(
                power=self.power,
                lambda_start=self.w_start,
                lambda_stop=self.w_stop,
                lambda_step=self.w_step,
                lambda_speed=self.w_speed,
                cycles=self.cycles,
                )
            
            export_to_csv(data=self.df, filename=join(self.folder, f"{self.fname}.csv"))
        
        pm.set_volt(0)
        pm.set_output_state(0)


    def run_one_source_mzi(self):
        """ Run only with instrument. Require one voltage source """
        self.instrment_check(("pm", "mm"), self._addrs.keys())
        pm = AgilentE3640A(addr=self._addrs["pm"], rm=self._rm)
        mm = Agilent8164B(addr=self._addrs["mm"], rm=self._rm)
        avg = 3
        tol = 0.00005

        voltages = np.arange(self.v_start, self.v_stop+self.v_step, self.v_step)
        powers = []
        currs = []
        pm.set_output_state(1)
        pm.set_params(self.v_stop, 0.5)

        for volt in tqdm(voltages):
            prev_curr = 1000000
            pm.set_volt(volt)
            power = 0
            
            # wait until the current is stable
            while np.abs(pm.get_curr() - prev_curr) > tol:
                prev_curr = pm.get_curr()
                continue

            for _ in range(avg):
                power += mm.get_detect_pow()
            powers.append(power/avg)
            currs.append(prev_curr)

        pm.set_volt(0)
        pm.set_output_state(0)

        self.df["Voltage [V]"] = voltages
        self.df["Power [W]"] = powers
        self.df["Current [A]"] = currs
        export_to_csv(data=self.df, filename=join(self.folder, f"{self.fname}.csv"))


    def run_ring_assisted_mzi(self):
        """ 
        Try to see how the output power of a specific wavelength
        changes with the voltage of the MZI and the ring.
        """
        self.instrment_check(("pm", "mm"), self._addrs.keys())
        heater_pm = AgilentE3640A(addr=self._addrs["pm"][0], rm=self._rm)
        ring_pm = AgilentE3640A(addr=self._addrs["pm"][1], rm=self._rm)
        mm = Agilent8164B(addr=self._addrs["mm"], rm=self._rm)
    
        ilme = KeysightILME()
        ilme.activate()
        avg = 3

        tol = 0.00005

        ring_vstart = 0
        ring_vstop = 3
        ring_vstep = 0.5

        voltages = np.arange(self.v_start, self.v_stop+self.v_step, self.v_step)
        ring_voltages = np.arange(ring_vstart, ring_vstop+ring_vstep, ring_vstep)
        heater_pm.set_output_state(1)
        heater_pm.set_params(self.v_stop, 0.5)
        ring_pm.set_output_state(1)
        ring_pm.set_params(ring_vstop, 0.1)

        
        max_min_voltages = np.zeros(shape=(len(ring_voltages), 3))
        for i, ring_v in tqdm(enumerate(ring_voltages), total=len(ring_voltages)):
            powers = []
            currs = []
            
            ring_pm.set_volt(ring_v)

            mm.setup(0, 1550, 10, 0.2)

            for j, volt in enumerate(voltages):
                prev_curr = 1000000
                heater_pm.set_volt(volt)
                
                # wait until the current is stable
                while np.abs(heater_pm.get_curr() - prev_curr) > tol:
                    prev_curr = heater_pm.get_curr()
                    continue

                power = 0
                for _ in range(avg):
                    power += mm.get_detect_pow()
                powers.append(power/avg)
                currs.append(prev_curr)
            self.df["Voltage [V]"] = voltages
            self.df["Power [W]"] = powers
            self.df["Current [A]"] = currs
            export_to_csv(data=self.df, filename=join(self.folder, f"{self.fname}_ring{ring_v}_heater_{volt}.csv"))
            
            
            max_v = voltages[np.argmax(powers)]
            min_v = voltages[np.argmin(powers)]
            max_min_voltages[i] = [ring_v, max_v, min_v]
        
        np.savetxt(join(self.folder, f"{self.fname}_max_min_voltages.csv"), max_min_voltages, delimiter=",")
        heater_pm.set_volt(0)
        heater_pm.set_output_state(0)
        ring_pm.set_volt(0)
        ring_pm.set_output_state(0)


def run_ring_assisted_mzi():
    import pyvisa
    rm = pyvisa.ResourceManager()
    sweep = DCSweeps(
        ttype_configs=DictObj(**{
            "v_start": 0,
            "v_stop": 2,
            "v_step": 0.01,
            "cycles": 1,
            "lambda_start": 1530,
            "lambda_stop": 1570,
            "lambda_step": 0.1,
            "lambda_speed": "auto",
            "power": 13,
            "omr_save": True,
        }),
        addrs={
            "pm": ["GPIB0::6::INSTR", "GPIB0::5::INSTR"],
            "mm": "GPIB0::20::INSTR",
        },
        rm=rm,
        folder="2024-4-19-ring-assisted-mzi-find-mixmax-g220",
        fname="",
    )

    makedirs(sweep.folder, exist_ok=True)

    sweep.run_ring_assisted_mzi()

def run_ilme_main():
    import pyvisa
    rm = pyvisa.ResourceManager()
    sweep = DCSweeps(
        ttype_configs=DictObj(**{
            "v_start": 0,
            "v_stop": 3,
            "v_step": 0.5,
            "lambda_start": 1530,
            "lambda_stop": 1570,
            "lambda_step": 0.1,
            "lambda_speed": "auto",
            "cycles": 1,
            "power": 13,
            "omr_save": True,
        }),
        addrs={
            "pm": "GPIB0::5::INSTR",
        },
        rm=rm,
        folder="2024-4-19-ring-dc-sweep",
        fname="",
    )

    makedirs(sweep.folder, exist_ok=True)

    sweep.run_ilme()

def main():

    import pyvisa
    
    rm = pyvisa.ResourceManager()
    sweep = DCSweeps(
        ttype_configs=DictObj(**{
            "v_start": 0,
            "v_stop": 3,
            "v_step": 0.01,
            "cycles": 1,
            "lambda_start": 1520,
            "lambda_stop": 1580,
            "lambda_step": 0.1,
            "lambda_speed": 0.1,
            "power": 13,
            "omr_save": True,
        }),
        addrs={
            "pm": "GPIB0::6::INSTR",
            "mm": "GPIB0::20::INSTR",
        },
        rm=rm,
        folder=".",
        fname="DCSweep"
    )

    sweep.run_one_source_mzi()

if __name__ == "__main__":
    run_ring_assisted_mzi()  
