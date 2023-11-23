import numpy as np
import math
import pandas as pd

from pyoctal.instruments import AgilentE3640A, Agilent8163B
from pyoctal.base import BaseSweeps
from pyoctal.util.file_operations import export_to_csv

class PulseSweeps(BaseSweeps):
    """
    Pulse Sweeps

    This sweeps through the voltage range and obtains the information
    about the insertion loss against wavelength 

    Parameters
    ----------
    ttype_configs: dict
        Test type specific configuration parameters
    instr_addrs: map
        All instrument addresses
    rm:
        Pyvisa resource manager
    folder: str
        Path to the folder
    fname: str
        Filename
    """
    def __init__(self, ttype_configs: dict, instr_addrs: dict, rm, folder: str, fname: str):
        super().__init__(instr_addrs=instr_addrs, rm=rm, folder=folder, fname=fname)
        self.wavelength = ttype_configs.wavelength*1e-09
        self.avg_pts = ttype_configs.avg_pts
        self.v_start = ttype_configs.v_start
        self.v_stop = ttype_configs.v_stop
        self.cycle = ttype_configs.cycle
        self.channel = ttype_configs.channel
        self.avg_transmission_at_quad = ttype_configs.avg_transmission_at_quad
        self.current_fname = ttype_configs.current_filename
        self.power_fname = ttype_configs.power_filename
        self.phase_fname = ttype_configs.phase_filename

    @staticmethod
    def phase_calculation(
        power: float,
        transmission: float,
        prev_phase: float,
        prev_phase_change: float
        ):
        data = power/transmission - 1
        data = 1 if data > 1 else -1 if data < -1 else data
        phase = math.acos(data)
        phase_change = abs(phase - prev_phase)
        phase_change_avg = (prev_phase_change + phase_change)/2

        return phase, phase_change, phase_change_avg

    @staticmethod
    def step_amount_calculation(phase_change_avg: float):
        # Change step_V depending on average phase change
        if phase_change_avg <= 0.005:
            return 0.025
        elif 0.005 < phase_change_avg <=0.01:
            return 0.005
        elif 0.01 < phase_change_avg < 0.03:
            return 0.0025
        else:
            return 0.001

    def get_pulse_response_sw(self):
        """ Get pulse response at a single wavelength. """
        mm = Agilent8163B(addr=self._addrs.mm, rm=self._rm)
        pm = AgilentE3640A(addr=self._addrs.pm, rm=self._rm)

        mm.set_detect_autorange(auto=True)
               
        volt_curr_data = []
        powers = []
        phases = []

        counter = 0
        volt = self.v_start
        while volt < self.v_stop:
            for _ in range(self.cycle):
                pm.set_channel(self.channel, volt, 20e-03)
                volt, curr = pm.read_channel_data(self.channel)
                volt_curr_data.append([volt, curr])
                pm.set_channel(self.channel, 0, 0)

                power = []
                for _ in range(self.avg_pts):
                    power.append(float(mm.get_detect_power().rstrip()))
                current_power = math.fsum(power)/self.avg_pts
                powers.append(powers)


                phase, phase_change, phase_change_avg = self.phase_calculation(current_power, self.avg_transmission_at_quad, last_phase, last_phase_change)
                phases.append([counter, volt, phase, phase_change, phase_change_avg])

                step_amount = self.step_amount_calculation(phase_change_avg)

                counter += 1
                volt += step_amount
                last_phase_change = phase_change
                last_phase = phase

        np.savetxt(self.current_fname, volt_curr_data, delimiter=",")
        np.savetxt(self.power_fname, powers, delimiter=",")
        df = pd.DataFrame(phases, columns=["Measurement Number", "Voltage applied", " Current phase", "Phase change", "Phase change average"])
        df.to_csv(self.phase_fname, index=False)