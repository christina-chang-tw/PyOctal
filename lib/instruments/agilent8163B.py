from typing import Union
import sys
import time

from lib.base import BaseInstrument
from lib.error import PARAM_INVALID_ERR, error_message

class Agilent8163B(BaseInstrument):
    """
    Agilent 8163B Lightwave Multimeter VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    src_num: int, default: 1
        Source interface number
    src_chan: int, default: 1
        Source channel
    sens_num: int, default: 2
        Sensor interface number
    sens_chan: int, default: 1
        Sensor channel
    """
    def __init__(self, addr: str, src_num: int=1, src_chan: int=1, sens_num: int=2, sens_chan: int=1):
        super().__init__(rsc_addr=addr)
        self.src_num = src_num
        self.src_chan = src_chan
        self.sens_num = sens_num
        self.sens_chan = sens_chan
        self.laser = f"source{self.src_num}:channel{self.src_chan}"
        self.detect = f"sense{self.sens_num}:channel{self.sens_chan}"

    def setup(self, wavelength: float=1550, power: float=10, period: float=200e-03):
        """ Make waveguide alignment easier for users """
        self.reset()
        self.set_detect_autorange(1)
        self.set_wavelength(wavelength=wavelength)
        self.set_laser_pow(power)
        self.set_detect_avgtime(period=period) # avgtime = 200ms
        self.set_unit(source="dBm", sensor="Watt")
        self.set_laser_state(1)

    def unlock(self):
        self.write(f"lock {0},{1234}") # unlock with code 1234

    def set_wavelength(self, wavelength: float):
        wavelength = wavelength * 1e-09
        self.set_detect_wav(wavelength)
        self.set_laser_wav(wavelength)

    def set_unit(self, source: str, sensor: str):
        self.write(f"power:unit {source}") # set the source unit in dBm
        self.write(f"sense:power:unit {sensor}") # set sensor unit

    def set_trig_config(self, config: int):
        self.write(f"trigger:conf {config}")

    def set_trig_continuous_mode(self, status: bool):
        self.write(f"initiate{self.sens_num}:channel{self.sens_chan}:continuous {status}")



    ### DETECTOR COMMANDS ###############################
    def set_detect_avgtime(self, period: float):
        self.write(f"{self.detect}:power:atime {period}s")

    def set_detect_wav(self, wavelength: float):
        self.write(f"{self.detect}:power:wavelength {wavelength}")

    def set_detect_prange(self, prange: float):
        # set power range
        self.write(f"{self.detect}:power:range {prange}dBm")

    def set_detect_autorange(self, auto: bool):
        self.write(f"{self.detect}:power:range:auto {auto}")

    def set_detect_unit(self, unit: str):
        self.write(f"{self.detect}:power:unit {unit}") # set detector unit

    def set_detect_calibration_val(self, value: float):
        self.write(f"{self.detect}:correction {value}dB")

    def set_detect_trig_response(self, in_rsp: str, out_rsp: str):
        self.write(f"trigger{self.sens_num}:channel{self.sens_chan}:input {in_rsp}")
        self.write(f"trigger{self.src_num}:channel{self.sens_chan}:output {out_rsp}")

    def set_detect_func_mode(self, mode: Union[tuple,list]):
        self.write(f"{self.laser}:function:status {mode[0]},{mode[1]}")
    
    def set_detect_func_params(self, mode: str, params: Union[tuple,list]):
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
        return self.query_float(f"read{self.sens_num}:channel{self.sens_chan}:power?")
    
    def get_detect_trigno(self) -> int:
        return int(self.query(f"{self.detect}:wavelength:sweep:exp?"))
    
    def get_detect_func_state(self) -> bool:
        return bool(self.query(f"{self.detect}:function:state?"))
    
    def get_detect_func_result(self) -> list:
        return self.query_binary_values(f"{self.detect}:function:result?")



    ### LASER COMMANDS ###################################
    def set_laser_wav(self, wavelength: float):
        self.write(f"{self.laser}:wavelength {wavelength}")
    
    def set_laser_state(self, state: bool):
        self.write(f"{self.laser}:power:state {state}")

    def set_laser_pow(self, power: float):
        self.write(f"{self.laser}:power:level:immediate:amplitude {power}dBm")

    def set_laser_trig_response(self, in_rsp: str, out_rsp: str):
        self.write(f"trigger{self.src_num}:channel{self.src_chan}:input {in_rsp}")
        self.write(f"trigger{self.src_num}:channel{self.src_chan}:output {out_rsp}")

    def set_laser_unit(self, unit: str):
        self.write(f"{self.laser}:power:unit {unit}") # set the source unit in dBm

    def get_laser_data(self, mode: str) -> list:
        return self.query_binary_values(f"{self.laser}:read:data? {mode}")
    
    def get_laser_wav_min(self) -> float:
        return self.query_float(f"{self.laser}:wavelength? MIN")

    def get_laser_wav_max(self) -> float:
        return self.query_float(f"{self.laser}:wavelength? MAX")
    


    ### SWEEP COMMANDS ####################################
    def set_sweep_mode(self, mode: str): # STEP, MAN, CONT
        self.write(f"{self.laser}:sweep:mode {mode}")

    def set_sweep_state(self, state: Union[int, str]): # 0 - stop, 1 - start, 2 - pause, 3 - continue
        self.write(f"{self.laser}:wavelength:sweep:state {state}")

    def set_sweep_speed(self, speed: float):
        self.write(f"{self.laser}:wavelength:sweep:speed {speed}nm/s")

    def set_sweep_step(self, step: float):
        self.write(f"{self.laser}:wavelength:sweep:step {step}pm")

    def set_sweep_start_stop(self, start: float, stop: float):
        self.write(f"{self.laser}:wavelength:sweep:start {start}nm")
        self.write(f"{self.laser}:wavelength:sweep:stop {stop}nm")
    
    def set_sweep_wav_logging(self, status: bool):
        self.write(f"{self.laser}:wavelength:sweep:llogging {status}")

    def set_sweep_repeat_mode(self, mode: str):
        self.write(f"{self.laser}:wavelength:sweep:repeat {mode}")

    def set_sweep_cycles(self, cycles: int):
        self.write(f"{self.laser}:wavelength:sweep:cycles {cycles}")

    def set_sweep_tdwell(self, tdwell: float):
        self.write(f"{self.laser}:dwell {tdwell}s")
    
    def get_sweep_state(self) -> int: # 0 - stop, 1 - start, 2 - pause, 3 - continue
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









                

                



            

    