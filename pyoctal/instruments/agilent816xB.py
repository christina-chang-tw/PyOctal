from typing import Union
import sys
import time

import numpy as np
from scipy.signal import find_peaks

from pyoctal.base import BaseInstrument
from pyoctal.error import PARAM_INVALID_ERR, error_message
from pyoctal.util.util import dbm_to_watt


def resonances(data: np.array, cutoff: float, distance: int) -> list:
    """ 
    Find the resonances in the spectrum. 
    
    Parameters
    ----------
    cutoff: float
        The cutoff value to find the resonances
    distance: int
        The minimum distance between each peak

    Returns
    -------
    list
        The resonances found in the spectrum
    """
    peaks, _ = find_peaks(data, distance=distance)
    peaks = peaks[data[peaks] - min(data) > cutoff]
    return peaks
    


class Agilent816xB(BaseInstrument):
    """
    Agilent 816xB General VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    src_num: int
        Source interface number
    src_chan: int
        Source channel
    sens_num: int
        Sensor interface number
    sens_chan: int
        Sensor channel
    """
    def __init__(self, addr: str, rm, src_num: int, src_chan: int, sens_num: int, sens_chan: int):
        super().__init__(rsc_addr=addr, rm=rm)
        self.src_num = src_num
        self.src_chan = src_chan
        self.sens_num = sens_num
        self.sens_chan = sens_chan
        self.laser = f"source{self.src_num}:channel{self.src_chan}"
        self.detect = f"sense{self.sens_num}:channel{self.sens_chan}"

    def setup(self, reset: bool, wavelength: float=1550, power: float=10, period: float=200e-03):
        """ Make waveguide alignment easier for users """
        if reset:
            self.reset()
        self.set_detect_autorange(1)
        self.set_wavelength(wavelength=wavelength)
        self.set_laser_pow(power)
        self.set_detect_avgtime(period=period) # avgtime = 200ms
        self.set_unit(source="dBm", sensor="Watt")
        if not self.get_laser_state():
            self.set_laser_state(1)

    def unlock(self, code: str):
        """ Unlock the instrument with a code. """
        self.write(f"lock {0},{code}") # code = 1234

    def set_wavelength(self, wavelength: float):
        """ Set both laser and detector wavelength [nm]. """
        wavelength = wavelength * 1e-09
        self.set_detect_wav(wavelength)
        self.set_laser_wav(wavelength)

    def set_unit(self, source: str, sensor: str):
        """ Set the power unit of the laser and detector. """
        self.write(f"power:unit {source}") # set the source unit in dBm
        self.write(f"sense:power:unit {sensor}") # set sensor unit

    def set_trig_config(self, config: int):
        """ Set the configuration of trigger. """
        self.write(f"trigger:conf {config}")

    def set_trig_contmode_state(self, state: bool):
        """ Set the trigger continuous mode state. """
        self.write(f"initiate{self.sens_num}:channel{self.sens_chan}:continuous {state}")



    ### DETECTOR COMMANDS ###############################
    def set_detect_avgtime(self, period: float):
        """ Set the detector average time. """
        self.write(f"{self.detect}:power:atime {period}s")

    def set_detect_wav(self, wavelength: float):
        """ Set the detector wavelength. """
        self.write(f"{self.detect}:power:wavelength {wavelength}")

    def set_detect_prange(self, prange: float):
        """ Set the detector power range. """
        self.write(f"{self.detect}:power:range {prange}dBm")

    def set_detect_autorange(self, auto: bool):
        """ Set the detector power autorange. """
        self.write(f"{self.detect}:power:range:auto {auto}")

    def set_detect_unit(self, unit: str):
        """ Set the detector power unit. """
        self.write(f"{self.detect}:power:unit {unit}") # set detector unit

    def set_detect_calibration_val(self, value: float):
        """ Set the detector calibration value. """
        self.write(f"{self.detect}:correction {value}dB")

    def set_detect_trig_response(self, in_rsp: str, out_rsp: str):
        """ Set the detector trigger response for both input and output. """
        self.write(f"trigger{self.sens_num}:channel{self.sens_chan}:input {in_rsp}")
        self.write(f"trigger{self.src_num}:channel{self.sens_chan}:output {out_rsp}")

    def set_detect_func_mode(self, mode: Union[tuple,list]):
        """ Set the detector function status. """
        self.write(f"{self.laser}:function:status {mode[0]},{mode[1]}")
    
    def set_detect_func_params(self, mode: str, params: Union[tuple,list]):
        """ Set the detector function parameters. """
        mode = mode.lower()
        if mode == "logging" or "logg": # params = [data_pts, avg_time]
            self.write(f"{self.detect}:function:parameter:logging {params[0]},{params[1]}s") 
        elif mode == "minmax" or "minm": # params = [mode, data_pts]
            self.write(f"{self.detect}:function:parameter:minmax {params[0]},{params[1]}") 
        elif mode == "stability" or "stab": # params = [total_time, period, avg_time]
            self.write(f"{self.detect}:function:parameter:stability {params[0]}s,{params[1]}s,{params[2]}s") 
        else:
            raise ValueError(f"Error code {PARAM_INVALID_ERR:x}: {error_message[PARAM_INVALID_ERR]}")


    def get_detect_pow(self) -> float:
        """ Get the detector power. """
        return self.query_float(f"read{self.sens_num}:channel{self.sens_chan}:power?")
    
    def get_detect_trigno(self) -> int:
        """ Get the detector trigger number. """
        return int(self.query(f"{self.detect}:wavelength:sweep:exp?"))
    
    def get_detect_func_state(self) -> bool:
        """ Get the detector function state. """
        return bool(self.query(f"{self.detect}:function:state?"))
    
    def get_detect_func_result(self) -> list:
        """ Get the detector function result. """
        return self.query_binary_values(f"{self.detect}:function:result?")



    ### LASER COMMANDS ###################################
    def set_laser_wav(self, wavelength: float):
        """ Set the laser wavelength. """
        self.write(f"{self.laser}:wavelength {wavelength}")
    
    def set_laser_state(self, state: bool):
        """ Set the laser output state. """
        self.write(f"{self.laser}:power:state {state}")

    def set_laser_pow(self, power: float):
        """ Set the laser power [dBm]. """
        self.write(f"{self.laser}:power:level:immediate:amplitude {power}dBm")

    def set_laser_trig_response(self, in_rsp: str, out_rsp: str):
        """ Set the laser trigger response. """
        self.write(f"trigger{self.src_num}:channel{self.src_chan}:input {in_rsp}")
        self.write(f"trigger{self.src_num}:channel{self.src_chan}:output {out_rsp}")

    def set_laser_unit(self, unit: str):
        """ Set the laser unit. """
        self.write(f"{self.laser}:power:unit {unit}") # set the source unit in dBm

    def get_laser_data(self, mode: str) -> list:
        """ Get the laser data. """
        return self.query_binary_values(f"{self.laser}:read:data? {mode}")
    
    def get_laser_state(self) -> bool:
        """ Get the laser output state. """
        self.query_bool(f"{self.laser}:power:state?")
    
    def get_laser_wav_min(self) -> float:
        """ Get the laser's minimum wavelength. """
        return self.query_float(f"{self.laser}:wavelength? MIN")

    def get_laser_wav_max(self) -> float:
        """ Get the laser's maximum wavelength. """
        return self.query_float(f"{self.laser}:wavelength? MAX")
    


    ### SWEEP COMMANDS ####################################
    def set_sweep_mode(self, mode: str): # STEP, MAN, CONT
        """ Set the sweep mode. """
        self.write(f"{self.laser}:sweep:mode {mode}")

    def set_sweep_state(self, state: Union[int, str]): # 0 - stop, 1 - start, 2 - pause, 3 - continue
        """ Set the sweep state. """
        self.write(f"{self.laser}:wavelength:sweep:state {state}")

    def set_sweep_speed(self, speed: float):
        """ Set the sweep speed [nm/s]. """
        self.write(f"{self.laser}:wavelength:sweep:speed {speed}nm/s")

    def set_sweep_step(self, step: float):
        """ Set the sweep step [pm]. """
        self.write(f"{self.laser}:wavelength:sweep:step {step}pm")

    def set_sweep_start_stop(self, start: float, stop: float):
        """ Set the start and stop wavelength sweep [nm]. """
        self.write(f"{self.laser}:wavelength:sweep:start {start}nm")
        self.write(f"{self.laser}:wavelength:sweep:stop {stop}nm")
    
    def set_sweep_wav_logging(self, status: bool):
        """ Set the logging for the sweep. """
        self.write(f"{self.laser}:wavelength:sweep:llogging {status}")

    def set_sweep_repeat_mode(self, mode: str):
        """ Set the sweep repeat mode. """
        self.write(f"{self.laser}:wavelength:sweep:repeat {mode}")

    def set_sweep_cycles(self, cycles: int):
        """ Set the sweep cycles. """
        self.write(f"{self.laser}:wavelength:sweep:cycles {cycles}")

    def set_sweep_tdwell(self, tdwell: float):
        """ Set the dwelling time for the laser. """
        self.write(f"{self.laser}:dwell {tdwell}s")
    
    def get_sweep_state(self) -> int: # 0 - stop, 1 - start, 2 - pause, 3 - continue
        """ Get the sweep state. """
        return int(self.query(f"{self.laser}:wavelength:sweep:state?"))
        

    # Complicated functions
    def run_sweep_manual(self, power: float=10.0, lambda_start: float=1535.0, lambda_stop: float=1575.0, lambda_step: float=5.0):
        """ Step through each wavelength purely by changing the output laser wavelength. """
        lambda_range = (self.get_laser_wav_min(), self.get_laser_wav_min())
        if lambda_start <= lambda_range[0] and lambda_stop >= lambda_range[1]:
            raise ValueError(f"Wavelength out of range. Please be within {lambda_range[0]} and {lambda_range[1]}.")
        
        wavelengths = []
        powers = []
        self.set_detect_autorange(1)
        self.set_detect_avgtime(200e-03)
        self.set_laser_pow(power)

        for wavelength in range(lambda_start, lambda_stop + lambda_step, lambda_step):
            tolerance = 0.001 # detector stability tolerance
            diff = prev_power = sys.maxsize
            loop_max = 20

            self.set_wavelength(wavelength)

            # Make sure that the laser power is stabalised
            for _ in range(loop_max):
                time.sleep(0.5)
                detected_power = float(self.get_detect_pow())
                diff = (detected_power - prev_power)/detected_power
                prev_power = detected_power
                if abs(diff) <= tolerance:
                    break

            wavelengths.append(wavelength)
            powers.append(detected_power)

            return wavelengths, powers
        

    def run_laser_sweep_auto(self, power: float=10.0, lambda_start: float=1535.0, lambda_stop: float=1575.0, lambda_step: float=5.0, cycles: int=1, tavg: float=100, lambda_speed: float=5):
        """ Use internal sweep module to sweep through wavelengths. """
        self.set_unit(source="dBm", sensor="Watt")

        self.set_laser_pow(power=power)
        self.set_laser_wav(wavelength=lambda_start)
        self.set_laser_state(state=1)
        

        self.set_detect_wav(wavelength=1550)
        self.set_detect_avgtime(period=1e-04)
        self.set_detect_calibration_val(value=0)
        self.set_detect_autorange(auto=0)
        self.set_detect_prange(prange=10)

        self.set_trig_config(config=3)
        self.set_laser_trig_response(in_rsp="ignored", out_rsp="stfinished")
        self.set_detect_trig_response(in_rsp="smeasure", out_rsp="disabled")
        
        self.set_sweep_mode(mode="continuous")
        self.set_sweep_repeat_mode(mode="oneway")
        self.set_sweep_cycles(cycles=cycles)
        self.set_sweep_tdwell(tdwell=0)
        self.set_sweep_start_stop(start=lambda_start, stop=lambda_stop)
        self.set_sweep_step(step=lambda_step)
        self.set_sweep_speed(speed=lambda_speed)
        
        self.set_detect_func_mode(mode=("logging", "stop"))
        trigno = self.get_detect_trigno()
        self.set_detect_func_params(mode="logging", params=(trigno, tavg*1e-06))
        self.set_detect_func_mode(mode=("logging", "start"))
        
        self.set_sweep_state(state="start")

        # wait for the sweep to finish
        while self.get_sweep_state():
            pass

        # Wait until the detector data acquisition is completed
        while self.get_detect_func_state().endswith("progress"):
            time.sleep(0.1)

        results = self.get_detect_func_result()
        self.set_detect_func_mode(mode=("logging","stop"))

        return results
   

    def find_op_wavelength(self, db: float, target: float, xrange: float=20e-09,
                           step: float=5e-12, cutoff: float=10, distance: float=100, tol: float=1e-09) -> float:
        """
        Find the operating wavelength that corresponds to a certain dB point from the maximum power level.
        This wavelength should be on the lefthand side of the resonance and should be the closest to
        the target wavelength.

        Parameters
        ----------
        db: float
            The dB value from the normalised maximum value. i.e. db = -3, -3dB from 1.
        target: float
            The target value to find
        xrange: float
            The range of the wavelength to search.
            i.e. if xrange = 20e-09, the search range will be target - 10nm to target + 10nm
        step: float
            The step size of the wavelength search
        cutoff: float
            The cutoff value to find the resonances
        distance: float
            The minimum distance between each peak
        tol: float
            The tolerance value to find the closest wavelength
            
        Returns
        -------
        float
            The wavelength that corresponds to the target value
        """
        wavelengths = np.round(np.arange(target-xrange/2, target+xrange/2+step, step), 4)
        ratio = dbm_to_watt(db)

        result = np.zeros(shape=(len(wavelengths), 2), dtype=float)

        for idx, wavelength in enumerate(wavelengths):
            self.set_wavelength(wavelength=wavelength)
            power = self.get_detect_pow()
            result[idx] = (wavelength, power)

        peak_idxs = resonances(data=result[:,1], cutoff=cutoff, distance=distance)
        if len(peak_idxs) == 0:
            raise ValueError("No resonances found. Please adjust the parameters.")

        # Find the closest wavelength to the target
        hbd_idx = np.argmin(np.abs(result[:,0][peak_idxs] - target))
        lbd_idx = peak_idxs(np.where(peak_idxs == hbd_idx)[0][0]-1)
        result = result[lbd_idx:hbd_idx, lbd_idx:hbd_idx]

        pmax = np.max(result[:,1])
        ptarget = pmax*ratio
        # find the rightmost one as it will be on the lefthand side of the resonance
        target_idx = np.where(np.abs(result[:,1] - pmax - ptarget) <= tol)[-1]

        return result[:,0][target_idx]


class Agilent8163B(Agilent816xB):
    """
    Agilent 8163B Lightwave Multimeter VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    src_num: int, default: 1
        Source interface number
    src_chan: int, default: 1
        Source channel
    sens_num: int, default: 2
        Sensor interface number
    sens_chan: int, default: 1
        Sensor channel
    """
    def __init__(self, addr: str, rm, src_num: int=1, src_chan: int=1, sens_num: int=2, sens_chan: int=1):
        super().__init__(
            addr=addr, 
            rm=rm, 
            src_num=src_num, 
            src_chan=src_chan, 
            sens_num=sens_num, 
            sens_chan=sens_chan
        )

class Agilent8164B(Agilent816xB):
    """
    Agilent 8164B Lightwave Measurement VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    src_num: int, default: 0
        Source interface number
    src_chan: int, default: 1
        Source channel
    sens_num: int, default: 2
        Sensor interface number
    sens_chan: int, default: 1
        Sensor channel
    """
    def __init__(self, addr: str, rm, src_num: int=0, src_chan: int=1, sens_num: int=2, sens_chan: int=1):
        super().__init__(
            addr=addr, 
            rm=rm, 
            src_num=src_num, 
            src_chan=src_chan, 
            sens_num=sens_num, 
            sens_chan=sens_chan
        )










                

                



            

    