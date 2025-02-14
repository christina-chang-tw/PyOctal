"""
Pulse Sweeps

This sweeps through the voltage range and obtains the information
about the insertion loss against wavelength .
"""
import math

import numpy as np
import pandas as pd
from pyvisa import ResourceManager

from pyoctal.instruments import AgilentE3640A, Agilent8163B


def phase_calculation(
    power: float,
    transmission: float,
    prev_phase: float,
    prev_phase_change: float
    ):
    """
    Calculate the phase and phase change.
    """
    data = power/transmission - 1
    data = 1 if data > 1 else -1 if data < -1 else data
    phase = math.acos(data)
    phase_change = abs(phase - prev_phase)
    phase_change_avg = (prev_phase_change + phase_change)/2

    return phase, phase_change, phase_change_avg

def step_amount_calculation(phase_change_avg: float):
    """
    Adjust the step amount depending on the average phase change.
    """
    # Change step_V depending on average phase change
    if phase_change_avg <= 0.005:
        return 0.025
    if 0.005 < phase_change_avg <=0.01:
        return 0.005
    if 0.01 < phase_change_avg < 0.03:
        return 0.0025
    return 0.001

def get_pulse_response_sw(rm: ResourceManager, mm_config: dict, pm_config: dict):
    """ Get pulse response at a single wavelength. """
    mm = Agilent8163B(rm=rm)
    mm.connect(addr=mm_config["addr"])
    pm = AgilentE3640A(rm=rm)
    pm.connect(addr=pm_config["addr"])

    mm.set_detect_autorange(auto=True)
    mm.set_wavelength(mm_config["wavelength"])

    volt_curr_data = []
    powers = []
    phases = []

    counter = 0
    volt = pm_config["start"]
    while volt < pm_config["stop"]:
        for _ in range(pm_config["cycle"]):
            pm.set_channel(pm_config["channel"], volt, 20e-03)
            volt, curr = pm.read_channel_data(pm_config["channel"])
            volt_curr_data.append([volt, curr])
            pm.set_channel(pm_config["channel"], 0, 0)

            power = []
            for _ in range(pm_config["avg_pts"]):
                power.append(float(mm.get_detect_power().rstrip()))
            current_power = math.fsum(power)/pm_config["avg_pts"]
            powers.append(powers)


            phase, phase_change, phase_change_avg = phase_calculation(
                current_power, pm_config["avg_transmission_at_quad"],last_phase, last_phase_change
            )
            phases.append([counter, volt, phase, phase_change, phase_change_avg])

            step_amount = step_amount_calculation(phase_change_avg)

            counter += 1
            volt += step_amount
            last_phase_change = phase_change
            last_phase = phase

    return volt_curr_data, powers, phases

def main():
    """ Entry point."""
    mm_config = {
        "addr": "GPIB0::20::INSTR",
        "wavelength": 1550, # [nm]
    }
    pm_config = {
        "addr": "GPIB0::5::INSTR",
        "start": 0, # [V]
        "stop": 5, # [V]
        "cycle": 1,
        "channel": 1,
        "avg_pts": 10,
        "avg_transmission_at_quad": 0.5,
    }
    current_fname = "current.csv"
    power_fname = "power.csv"
    phase_fname = "phase.csv"

    rm = ResourceManager()
    volt_curr_data, powers, phases = get_pulse_response_sw(rm, mm_config, pm_config)

    np.savetxt(current_fname, volt_curr_data, delimiter=",")
    np.savetxt(power_fname, powers, delimiter=",")
    pd.DataFrame(
        phases,
        columns=["Measurement Number", "Voltage applied",
                 "Current phase", "Phase change", "Phase change average"]
    ).to_csv(phase_fname, index=False)
    rm.close()


if __name__ == "__main__":
    main()
