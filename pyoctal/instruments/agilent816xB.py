from typing import Union, List, Tuple
import sys
import time

import numpy as np
from scipy.signal import find_peaks

from pyoctal.instruments.base import BaseInstrument
from pyoctal.utils.error import PARAM_INVALID_ERR, error_message


def resonances(data: np.array, cutoff: float, distance: int) -> List:
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
    List
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
    def __init__(self, addr: str, rm, src_num: int,
                 src_chan: int, sens_num: int, sens_chan: int):
        super().__init__(rsc_addr=addr, rm=rm)
        self.src_num = src_num
        self.src_chan = src_chan
        self.sens_num = sens_num
        self.sens_chan = sens_chan
        self.laser = f"source{self.src_num}:channel{self.src_chan}"
        self.detect = f"sense{self.sens_num}:channel{self.sens_chan}"

    def setup(self, reset: bool, wavelength: float=1550,
              power: float=10, period: float=200e-03):
        """ Make waveguide alignment easier for users """
        if reset:
            self.reset()

        if not self.get_laser_state():
            self.set_laser_state(1)

        self.set_detect_autorange(1)
        self.set_wavelength(wavelength=wavelength)
        self.set_laser_pow(power)
        self.set_detect_avgtime(period=period) # avgtime = 200ms
        self.set_unit(source="dBm", sensor="Watt")
        if not self.get_laser_state():
            self.unlock("1234")
            self.set_laser_state(1)

    def unlock(self, code: str):
        """ Unlock the instrument with a code. """
        self.write(f"lock 0,{code}") # code = 1234

    def set_wavelength(self, wavelength: float):
        """ Set both laser and detector wavelength [nm]. """
        self.set_detect_wav(wavelength)
        self.set_laser_wav(wavelength)

    def set_unit(self, source: str, sensor: str):
        """ Set the power unit of the laser and detector. """
        self.write(f"{self.laser}:power:unit {source}") # set the source unit in dBm
        self.write(f"{self.detect}:power:unit {sensor}") # set sensor unit


    ### DETECTOR COMMANDS ###############################
    def set_detect_avgtime(self, period: float):
        """ Set the detector average time [s]. """
        self.write(f"{self.detect}:power:atime {period}s")

    def set_detect_wav(self, wavelength: float):
        """ Set the detector wavelength [nm]. """
        self.write(f"{self.detect}:power:wavelength {wavelength}nm")

    def set_detect_prange(self, prange: float):
        """ Set the detector power range [dBm]. """
        self.write(f"{self.detect}:power:range {prange}dBm")

    def set_detect_autorange(self, auto: bool):
        """ Set the detector power autorange. """
        self.write(f"{self.detect}:power:range:auto {auto}")

    def set_detect_unit(self, unit: str):
        """ Set the detector power unit. """
        self.write(f"{self.detect}:power:unit {unit}") # set detector unit

    def set_detect_calibration_val(self, value: float):
        """ Set the detector calibration value [dB]. """
        self.write(f"{self.detect}:correction {value}dB")

    def set_detect_func_mode(self, mode: Union[Tuple, List]):
        """ Set the detector function status. """
        self.write(f"{self.detect}:function:state {mode[0]},{mode[1]}")

    def set_detect_func_params(self, mode: str, params: Union[Tuple, List]):
        """ Set the detector function parameters. """
        mode = mode.lower()
        if mode in ("logging", "logg"): # params = [data_pts, avg_time]
            self.write(f"{self.detect}:function:parameter:logging {params[0]},{params[1]}s")
        elif mode in ("minmax", "minm"): # params = [mode, data_pts]
            self.write(f"{self.detect}:function:parameter:minmax {params[0]},{params[1]}")
        elif mode in ("stability", "stab"): # params = [total_time, period, avg_time]
            self.write(f"{self.detect}:function:parameter \
                       :stability {params[0]}s,{params[1]}s,{params[2]}s")
        else:
            raise ValueError(
                f"Error code {PARAM_INVALID_ERR:x}: {error_message[PARAM_INVALID_ERR]}"
            )


    def get_detect_pow(self) -> float:
        """ Get the detector power. """
        return self.query_float(f"read{self.sens_num}:channel{self.sens_chan}:power?")

    def get_trigno(self) -> int:
        """ Get the detector trigger number. """
        return int(self.query("source:channel:wavelength:sweep:exp?"))

    def get_detect_func_state(self) -> str:
        """ Get the detector function state. """
        rsp = self.query(f"{self.detect}:function:state?")
        return rsp.lower()

    def get_detect_func_result(self) -> List:
        """ Get the detector function result. """
        return self.query_binary_values(f"{self.detect}:function:result?")

    def get_detect_func_result_block(self, offset: int, dpts: int) -> List:
        """ Get the detector function result. """
        return self.query_binary_values(
            f"{self.detect}:function:result:block? {offset},{dpts}", datatype="d"
        )

    ### LASER COMMANDS ###################################
    def set_laser_am_state(self, state: bool):
        """ Set the laser amplitude modulation state. """
        self.write(f"{self.laser}:am:state {state}")

    def set_laser_wav(self, wavelength: float):
        """ Set the laser wavelength [nm]. """
        self.write(f"{self.laser}:wavelength:fixed {wavelength}nm")
    
    def set_laser_state(self, state: bool):
        """ Set the laser output state. """
        self.write(f"{self.laser}:power:state {state}")

    def set_laser_pow(self, power: float):
        """ Set the laser power [dBm]. """
        self.write(f"{self.laser}:power:level:immediate:amplitude {power}dBm")

    def set_laser_unit(self, unit: str):
        """ Set the laser unit. """
        self.write(f"{self.laser}:power:unit {unit}") # set the source unit in dBm

    def get_laser_data(self, mode: str) -> List:
        """ Get the laser data. """
        return self.query_binary_values(f"{self.laser}:read:data? {mode}", datatype="d")

    def get_laser_points(self, mode: str) -> int:
        """ Get the laser data points. """
        return int(self.query(f"{self.laser}:read:points? {mode}"))

    def get_laser_state(self) -> bool:
        """ Get the laser output state. """
        self.query_bool(f"{self.laser}:power:state?")

    def get_laser_wav_min(self) -> float:
        """ Get the laser's minimum wavelength. """
        return self.query_float(f"{self.laser}:wavelength? MIN")

    def get_laser_wav_max(self) -> float:
        """ Get the laser's maximum wavelength. """
        return self.query_float(f"{self.laser}:wavelength? MAX")

    def get_laser_wav(self) -> float:
        """ Get the laser wavelength. """
        return self.query_float(f"{self.laser}:wavelength?")

    ## TRIGGER COMMANDS ###################################
    def set_trig_config(self, config: int):
        """ Set the configuration of trigger. """
        self.write(f"trigger:conf {config}")

    def set_trig_contmode_state(self, num: int, chan: int, state: bool):
        """ Set the trigger continuous mode state. """
        self.write(f"initiate{num}:channel{chan}:continuous {state}")

    def set_trig_output(self, mode: str):
        """ Specify when an output trigger is generated. """
        self.write(f"trigger:output {mode}")

    def get_trig_output(self) -> str:
        """ Specify when an output trigger is generated. """
        return self.query("trigger:output?")

    def set_trig_responses(self, num: int, chan: int, in_rsp: str, out_rsp: str):
        """ Set the laser trigger response. """
        self.write(f"trigger{num}:channel{chan}:input {in_rsp}")
        self.write(f"trigger{num}:channel{chan}:output {out_rsp}")

    ### SWEEP COMMANDS ####################################
    def set_sweep_mode(self, mode: str): # STEP, MAN, CONT
        """ Set the sweep mode. """
        self.write(f"{self.laser}:sweep:mode {mode}")

    # 0 - stop, 1 - start, 2 - pause, 3 - continue
    def set_sweep_state(self, state: Union[int, str]):
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

    def set_sweep_soft_trig(self):
        """ Set the soft trigger for the sweep. Doesn't cause a PM to take measurement. """
        self.write(f"{self.laser}:wavelength:sweep:softtrigger")

    def get_sweep_state(self) -> int: # 0 - stop, 1 - start, 2 - pause, 3 - continue
        """ Get the sweep state. """
        return int(self.query(f"{self.laser}:wavelength:sweep:state?"))

    def get_sweep_flag(self) -> bool:
        """ Get the sweep flag. """
        return self.query_bool(f"{self.laser}:wavelength:sweep:flag?")

    def get_sweep_trigno(self) -> int:
        """ Get the laser trigger number. """
        return int(self.query(f"{self.laser}:wavelength:sweep:exp?"))
    
    def find_resonance(self, srange: float=1e-09) -> float:
        """ Find the resonance wavelength based on the current wavelength. """
        curr_wav = self.get_laser_wav()

        # quick search for the resonance by finding the minimum
        # power value within the range of the current wavelength
        powers = []
        search_wavelengths = np.linspace(curr_wav-srange*2/3, curr_wav+srange*1/3, num=int(srange//5e-10+1))*1e+09
        for wavelength in search_wavelengths:
            self.set_wavelength(wavelength)
            powers.append(self.get_detect_pow())
        arg = np.argmin(powers)

        if arg == 0 or arg == len(powers)-1:
            print(powers)
            print("Warning: Resonance not found. Please adjust the search range.")

        return search_wavelengths[arg]



    # Complicated functions
    def run_sweep_manual(self, power: float=10.0, lambda_start: float=1535.0,
                         lambda_stop: float=1575.0, lambda_step: float=5.0):
        """ Step through each wavelength purely by changing the output laser wavelength. """
        lambda_range = (self.get_laser_wav_min(), self.get_laser_wav_min())
        if lambda_start <= lambda_range[0] and lambda_stop >= lambda_range[1]:
            raise ValueError(
                f"Wavelength out of range. \
                Please be within {lambda_range[0]} and {lambda_range[1]}."
            )

        wavelengths = []
        powers = []
        self.set_detect_autorange(1)
        self.set_detect_avgtime(200e-03)
        self.set_laser_pow(power)
        self.set_detect_autorange(1)

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


    def run_laser_sweep_auto(self, power: float=None, start: float=1535.0,
                             stop: float=1575.0, step: float=5.0, cycles: int=1,
                             tavg: float=0, speed: float=5) -> np.array:
        """ 
        Use internal sweep module to sweep through wavelengths. 
        
        Parameters
        ----------
        power: float
            The laser power. If not provided, use the current setting.
        start: float
            The start wavelength in nm
        stop: float
            The stop wavelength in nm
        step: float
            The step wavelength in pm
        speed: float
            The speed of sweep in nm/s
        cycles: float
            The number of cycles
        tavg: float
            Averaging time in s
        
        Return
        ------
        np.array: 
            An array of detected laser power
        """
        self.set_unit(source="dBm", sensor="Watt")

        # laser setup
        if power is None:
            self.set_laser_pow(power=power)
        self.set_laser_wav(wavelength=start)
        self.set_laser_state(state=1)
        self.set_laser_am_state(0)

        # detector setup
        self.set_detect_func_mode(mode=("logging", "stop"))
        self.set_detect_wav(wavelength=1550)
        self.set_detect_avgtime(period=1e-04)
        self.set_detect_autorange(1)

        # trigger setup
        self.set_trig_config(config="loop")
        self.set_trig_responses(self.src_num, self.src_chan,
                                in_rsp="ignored", out_rsp="stfinished")
        self.set_trig_responses(self.sens_num, self.sens_chan,
                                in_rsp="smeasure", out_rsp="disabled")

        # sweep setup
        self.set_sweep_mode(mode="continuous")
        self.set_sweep_repeat_mode(mode="oneway")
        self.set_sweep_cycles(cycles=cycles)
        self.set_sweep_tdwell(tdwell=1e-04)
        self.set_sweep_start_stop(start=start, stop=stop)
        self.set_sweep_step(step=step)
        self.set_sweep_speed(speed=speed)
        self.set_sweep_wav_logging(status=1)
        trigno = self.get_sweep_trigno()

        self.set_detect_func_params(mode="logging", params=(trigno, tavg))
        self.set_detect_func_mode(mode=("logging", "start"))

        self.set_sweep_state(state="start")


        # wait for the sweep to finish
        while self.get_sweep_state():
            continue

        # wait until all points are logged
        while self.get_laser_points(mode="llogging") < trigno:
            continue

        wavelengths = self.get_laser_data(mode="llogging")

        # Wait until the detector data acquisition is completed
        while self.get_detect_func_state().lower().endswith("progress"):
            time.sleep(0.1)

        powers = self.get_detect_func_result()
        self.set_detect_func_mode(mode=("logging","stop"))

        self.reset()

        return wavelengths, powers

    def find_op_wavelength(self, db: float, target: float, xrange: float=20e-09, speed: float=5,
                           step: float=5, cutoff: float=10, distance: float=100,
                           tol: float=1e-09) -> float:
        """
        Find the operating wavelength that corresponds to a certain dB point 
        from the maximum power level. This wavelength should be on the lefthand side of the 
        resonance and should be the closest to the target wavelength.

        Parameters
        ----------
        db: float
            The dB value from the normalised maximum value. i.e. db = -3.
        target: float [nm]
            The target value to find
        xrange: float [nm]
            The range of the wavelength to search.
            i.e. if xrange = 20e-09, the search range will be target - 10nm to target + 10nm
        step: float [pm]
            The step size of the wavelength search
        speed: float [nm/s]
            The speed of the sweep
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
        wavelengths, powers = self.run_laser_sweep_auto(
            start=target-xrange/2, stop=target+xrange/2, step=step, speed=speed)

        # convert to dB so resonances function will work
        powers = 10*np.log10(powers)

        peak_idxs = resonances(data=powers, cutoff=cutoff, distance=distance)

        if len(peak_idxs) == 0:
            raise ValueError("No resonances found. Please adjust the parameters.")

        # Find the closest wavelength to the target
        hbd_idx = np.argmin(np.abs(wavelengths[peak_idxs] - target))
        lbd_idx = peak_idxs(np.where(peak_idxs == hbd_idx)[0][0]-1)
        powers = powers[lbd_idx:hbd_idx]

        pmax = np.max(powers)
        ptarget = pmax - db

        # find the rightmost one as it will be on the lefthand side of the resonance
        target_idx = np.where(np.abs(powers - ptarget) <= tol)[-1] + lbd_idx

        return wavelengths[target_idx]

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
    def __init__(self, addr: str, rm, src_num: int=1,
                 src_chan: int=1, sens_num: int=2, sens_chan: int=1):
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
    def __init__(self, addr: str, rm, src_num: int=0,
                 src_chan: int=1, sens_num: int=2, sens_chan: int=1):
        super().__init__(
            addr=addr,
            rm=rm,
            src_num=src_num,
            src_chan=src_chan,
            sens_num=sens_num,
            sens_chan=sens_chan,
        )
