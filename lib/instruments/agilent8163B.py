from lib.instruments.base import BaseInstrument
import logging
import time
import pandas as pd
import sys

logger = logging.getLogger(__name__)

class Agilent8163B(BaseInstrument):
    """
    Instrument: 8163B Lightwave Multimeter
    
    Remote control the multimeter with this library
    """

    def __init__(self, addr: str="GPIB0::25::INSTR", src_num: int=1, src_chan: int=1, sens_num: int=2, sens_chan: int=1):
        super().__init__(rsc_addr=addr) 
        self.src_num = src_num
        self.src_chan = src_chan
        self.sens_num = sens_num
        self.sens_chan = sens_chan

    def setup(self, wavelength: float=1550, power: float=10):
        self.reset("*RST")
        self.set_detect_autorange(1)
        self.set_wavelength(wavelength=wavelength)
        self.set_laser_pow(pow(10, power/10)/1000)
        self.set_detect_avgtime(period=200e-03) # avgtime = 200ms
        self.set_unit(source="dBm", sensor="Watt")
        self.set_laser_state(1)

    def set_wavelength(self, wavelength: float):
        wavelength = wavelength * 1e-09
        self.set_detect_wav(wavelength)
        self.set_laser_wav(wavelength)

    def set_unit(self, source: str="dBm", sensor: str="Watt"):
        self.write(f"power:unit {source}") # set the source unit in dBm
        self.write(f"sense:power:unit {sensor}") # set sensor unit

    def unlock(self):
        self.write("lock 0,1234")

    def set_trig_config(self, config):
        self.write(f"trigger:conf {config}")

    def set_trig_continuous_mode(self, status: bool=1):
        self.write(f"initiate{self.sens_num}:channel{self.sens_chan}:continuous {status}")



    # Detector
    def set_detect_avgtime(self, period):
        self.write(f"sense{self.sens_num}:channel{self.sens_chan}:power:atime {period}s")

    def set_detect_wav(self, wavelength: float):
        self.write(f"sense{self.sens_num}:channel{self.sens_chan}:power:wavelength {wavelength}")

    def set_detect_prange(self, prange: float):
        # set power range
        self.write(f"sense{self.sens_num}:channel{self.sens_chan}:power:range {prange}dBm")

    def set_detect_autorange(self, auto: bool=1):
        self.write(f"sense{self.sens_num}:channel{self.sens_chan}:power:range:auto {auto}")

    def set_detect_unit(self, unit):
        self.write(f"sense{self.sens_num}:channel{self.sens_chan}:power:unit {unit}") # set sensor unit

    def set_detect_trig_response(self, in_rsp: str="smeasure", out_rsp: str="disabled"):
        self.write(f"trigger{self.sens_num}:channel{self.sens_chan}:input {in_rsp}")
        self.write(f"trigger{self.src_num}:channel{self.sens_chan}:output {out_rsp}")

    def set_detect_func_mode(self, mode: str):
        self.write(f"sense{self.sens_num}:channel{self.sens_chan}:function:status {mode[0]},{mode[1]}")

    def set_detect_calibration_val(self, value: float=0):
        self.write(f"sense{self.sens_num}:channel{self.sens_chan}:correction {value}dB")

    def set_detect_func_params(self, mode: str, params):
        mode = mode.lower()
        if mode == "logging" or "logg": # params = [data_pts, avg_time]
            self.write(f"sense{self.sens_num}:channel{self.sens_chan}:function:parameter:logging {params[0]},{params[1]}s") 
        elif mode == "minmax" or "minm": # params = [mode, data_pts]
            self.write(f"sense{self.sens_num}:channel{self.sens_chan}:function:parameter:minmax {params[0]},{params[1]}") 
        elif mode == "stability" or "stab": # params = [total_time, period, avg_time]
            self.write(f"sense{self.sens_num}:channel{self.sens_chan}:function:parameter:stability {params[0]}s,{params[1]}s,{params[2]}s") 

    def get_detect_pow(self):
        return self.query(f"read{self.sens_num}:channel{self.sens_chan}:power?")
    
    def get_detect_trigno(self):
        return self.query(f"sense{self.sens_num}:channel{self.sens_chan}:wavelength:sweep:exp?")



    # Laser
    def set_laser_wav(self, wavelength: float):
        self.write(f"source{self.src_num}:channel{self.src_chan}:wavelength {wavelength}")

    def get_laser_wav_min(self):
        return self.query(f"source{self.src_num}:channel{self.src_chan}:wavelength? MIN")

    def get_laser_wav_max(self):
        return self.query(f"source{self.src_num}:channel{self.src_chan}:wavelength? MAX")
    
    def set_laser_state(self, status: bool=1):
        self.write(f"source{self.src_num}:channel{self.src_chan}:power:state {status}")

    def set_laser_pow(self, power: float):
        self.write(f"source{self.src_num}:channel{self.src_chan}:power:level:immediate:amplitude {power}dBm")

    def set_laser_trig_response(self, in_rsp: str="ignore", out_rsp: str="stfinished"):
        self.write(f"trigger{self.src_num}:channel{self.src_chan}:input {in_rsp}")
        self.write(f"trigger{self.src_num}:channel{self.src_chan}:output {out_rsp}")

    def set_laser_unit(self, unit):
        self.write(f"source{self.src_num}:channel{self.src_chan}:power:unit {unit}") # set the source unit in dBm


    
    # Setting sweep parameters
    def set_sweep_mode(self, mode: str="CONT"): # STEP, MAN, CONT
        self.write(f"source{self.src_num}:channel{self.src_chan}:sweep:mode {mode}")

    def set_sweep_state(self, state: int=1): # 0 - stop, 1 - start, 2 - pause, 3 - continue
        self.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:state {state}")
    
    def set_sweep_step(self, step: float=5):
        self.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:step {step}pm")

    def set_sweep_start_stop(self, start: float, stop: float):
        self.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:start {start}nm")
        self.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:stop {stop}nm")
    
    def set_sweep_wav_logging(self, status: bool=1):
        self.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:llogging {status}")

    def set_sweep_repeat_mode(self, mode: str="oneway"):
        self.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:repeat {mode}")

    def set_sweep_cycles(self, cycles: int=1):
        self.write(f"source{self.src_num}:channel{self.src_chan}:wavelength:sweep:cycles {cycles}")

    def set_sweep_tdwell(self, time: float=0):
        self.write(f"source{self.src_num}:channel{self.src_chan}:dwell {time}s")

    
    # sweeps
    def run_laser_sweep_manual(self, power: float=10.0, start_lambda: float=1535.0, stop_lambda: float=1575.0, step: float=5.0):
        if start_lambda <= float(self.get_laser_wav_min()) and stop_lambda >= float(self.get_laser_wav_min()):
            sys.exit("Wavelength out of range")
        
        wavelengths = []
        powers = []
        self.set_detect_autorange(1)
        self.set_detect_avgtime(200e-03)
        self.set_laser_pow(power)

        #### Loop through wavelengths:
        for wavelength in range(start_lambda, stop_lambda + step, step):
            tolerance = 0.001 # detector stability tolerance
            diff = power_temp = sys.maxsize # initiation
            LOOP_MAX = 20

            self.set_wavelength(wavelength)
            
            # Make sure that the laser power is stabalised
            for _ in range(LOOP_MAX):
                time.sleep(0.5)
                detected_power = float(self.get_detect_pow())
                diff = (detected_power - power_temp)/detected_power
                power_temp = detected_power
                if abs(diff) <= tolerance:
                    break

            wavelengths.append(wavelength)
            powers.append(detected_power)

            return wavelengths, powers
        
    def run_laser_sweep_auto(self, power: float=10.0, start_lambda: float=1535.0, stop_lambda: float=1575.0, step: float=5.0, cycles: int=1, tavg: float=100):

        self.set_unit(source="dBm", sensor="Watt")

        self.set_laser_pow(power=power)
        self.set_laser_wav(wavelength=start_lambda)
        self.set_laser_state(status=1)
        

        self.set_detect_wav(wavelength=1550)
        self.set_detect_avgtime(period=1e-04)
        self.set_detect_calibration_val(value=0)
        self.set_detect_autorange(auto=0)
        self.set_detect_prange(range=10)

        self.set_trig_config(config=3)
        self.set_laser_trig_response(in_rsp="ignored", out_rsp="stfinished")
        self.set_detect_trig_response(in_rsp="smeasure", out_rsp="disabled")
        
        self.set_sweep_mode(mode="continuous")
        self.set_sweep_repeat_mode(mode="oneway")
        self.set_sweep_cycles(cycles=cycles)
        self.set_sweep_tdwell(time=0)
        self.set_sweep_start_stop(start=start_lambda, stop=stop_lambda)
        self.set_sweep_step(step=step)
        
        self.set_detect_func_mode(mode=("logging","stop"))
        trigno = self.get_detect_trigno()
        self.set_detect_func_params(mode="logging", params=(trigno, tavg*1e-06))








                

                



            

    