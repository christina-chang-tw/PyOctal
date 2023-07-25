from lib.base import BaseInstrument
from lib.error import *

from typing import Union

class Agilent8163B(BaseInstrument):
    """
    Agilent 8163B Lightwave Multimeter VISA Library

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
        self.reset()
        self.set_detect_autorange(1)
        self.set_wavelength(wavelength=wavelength)
        self.set_laser_pow(pow(10, power/10)/1000)
        self.set_detect_avgtime(period=period) # avgtime = 200ms
        self.set_unit(source="dBm", sensor="Watt")
        self.set_laser_state(1)

    def unlock(self):
        self.write(f"lock {0},{1234}") # unlock with code 1234

    def set_wavelength(self, wavelength: float):
        wavelength = wavelength * 1e-09
        self.set_detect_wav(wavelength)
        self.set_laser_wav(wavelength)

    def set_unit(self, source: str="dBm", sensor: str="Watt"):
        self.write(f"power:unit {source}") # set the source unit in dBm
        self.write(f"sense:power:unit {sensor}") # set sensor unit

    def set_trig_config(self, config):
        self.write(f"trigger:conf {config}")

    def set_trig_continuous_mode(self, status: bool=1):
        self.write(f"initiate{self.sens_num}:channel{self.sens_chan}:continuous {status}")



    ### DETECTOR ####################################
    def set_detect_avgtime(self, period):
        self.write(f"{self.detect}:power:atime {period}s")

    def set_detect_wav(self, wavelength: float):
        self.write(f"{self.detect}:power:wavelength {wavelength}")

    def set_detect_prange(self, prange: float):
        # set power range
        self.write(f"{self.detect}:power:range {prange}dBm")

    def set_detect_autorange(self, auto: bool=1):
        self.write(f"{self.detect}:power:range:auto {auto}")

    def set_detect_unit(self, unit: str="Watt"):
        self.write(f"{self.detect}:power:unit {unit}") # set detector unit

    def set_detect_calibration_val(self, value: float=0):
        self.write(f"{self.detect}:correction {value}dB")

    def set_detect_trig_response(self, in_rsp: str="smeasure", out_rsp: str="disabled"):
        self.write(f"trigger{self.sens_num}:channel{self.sens_chan}:input {in_rsp}")
        self.write(f"trigger{self.src_num}:channel{self.sens_chan}:output {out_rsp}")

    def set_detect_func_mode(self, mode: Union[tuple,list]):
        self.write(f"{self.sens}:function:status {mode[0]},{mode[1]}")
    
    def set_detect_func_params(self, mode: str, params: Union[tuple,list]):
        try: 
            mode = mode.lower()
            if mode == "logging" or "logg": # params = [data_pts, avg_time]
                self.write(f"{self.detect}:function:parameter:logging {params[0]},{params[1]}s") 
            elif mode == "minmax" or "minm": # params = [mode, data_pts]
                self.write(f"{self.detect}:function:parameter:minmax {params[0]},{params[1]}") 
            elif mode == "stability" or "stab": # params = [total_time, period, avg_time]
                self.write(f"{self.detect}:function:parameter:stability {params[0]}s,{params[1]}s,{params[2]}s") 
            else:
                raise ValueError(f"Error code {PARAM_INVALID_ERR:x}: {error_message[PARAM_INVALID_ERR]}")
        except Exception as e:
            print(e)

    def get_detect_pow(self):
        return self.query(f"read{self.sens_num}:channel{self.sens_chan}:power?")
    
    def get_detect_trigno(self):
        return self.query(f"{self.detect}:wavelength:sweep:exp?")
    
    def get_detect_func_status(self):
        return self.query(f"{self.detect}:function:state?")
    
    def get_detect_func_result(self):
        return self.query_binary_values(f"{self.detect}:function:result?")



    ### LASER ######################################
    def set_laser_wav(self, wavelength: float=1550):
        self.write(f"{self.laser}:wavelength {wavelength}")

    def get_laser_wav_min(self):
        return self.query(f"{self.laser}:wavelength? MIN")

    def get_laser_wav_max(self):
        return self.query(f"{self.laser}:wavelength? MAX")
    
    def set_laser_state(self, state: bool=1):
        self.write(f"{self.laser}:power:state {state}")

    def set_laser_pow(self, power: float=10):
        self.write(f"{self.laser}:power:level:immediate:amplitude {power}dBm")

    def set_laser_trig_response(self, in_rsp: str="ignore", out_rsp: str="stfinished"):
        self.write(f"trigger{self.src_num}:channel{self.src_chan}:input {in_rsp}")
        self.write(f"trigger{self.src_num}:channel{self.src_chan}:output {out_rsp}")

    def set_laser_unit(self, unit: str="dBm"):
        self.write(f"{self.laser}:power:unit {unit}") # set the source unit in dBm

    def get_laser_data(self, mode: str="lloging"):
        return self.query_binary_values(f"{self.laser}:read:data? {mode}")
    


    ### SWEEP ####################################
    def set_sweep_mode(self, mode: str="CONT"): # STEP, MAN, CONT
        self.write(f"{self.laser}:sweep:mode {mode}")

    def set_sweep_state(self, state: Union[int, str]): # 0 - stop, 1 - start, 2 - pause, 3 - continue
        self.write(f"{self.laser}:wavelength:sweep:state {state}")

    def set_sweep_speed(self, speed: float=50):
        self.write(f"{self.laser}:wavelength:sweep:speed {speed}nm/s")

    def set_sweep_step(self, step: float=5):
        self.write(f"{self.laser}:wavelength:sweep:step {step}pm")

    def set_sweep_start_stop(self, start: float=1535, stop: float=1575):
        self.write(f"{self.laser}:wavelength:sweep:start {start}nm")
        self.write(f"{self.laser}:wavelength:sweep:stop {stop}nm")
    
    def set_sweep_wav_logging(self, status: bool=1):
        self.write(f"{self.laser}:wavelength:sweep:llogging {status}")

    def set_sweep_repeat_mode(self, mode: str="oneway"):
        self.write(f"{self.laser}:wavelength:sweep:repeat {mode}")

    def set_sweep_cycles(self, cycles: int=1):
        self.write(f"{self.laser}:wavelength:sweep:cycles {cycles}")

    def set_sweep_tdwell(self, tdwell: float=0):
        self.write(f"{self.laser}:dwell {tdwell}s")
    
    def get_sweep_state(self): # 0 - stop, 1 - start, 2 - pause, 3 - continue
        return self.query(f"{self.laser}:wavelength:sweep:state?")
        











                

                



            

    