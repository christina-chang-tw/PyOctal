'''
Here contains all the dummy object class you can ever find in this repository!
This is created for testing purposes, so use this file if you want to test any function.
'''
import pandas as pd

class DummyMultimeter:

    def __init__(self, rm, addr, src_num, src_chan, sens_num, sens_chan):
        pass

    def setup(self, wavelength, power):
        pass

    def set_average_time(self):
        pass

    def _set_sens_wavelength(self, wavelength: float):
        pass
    def _set_src_wavelength(self, wavelength: float):
        pass

    # Setting the detector
    def set_power_range(self, prange: float): # in dBm
        pass

    def set_power_range_auto(self, auto: bool):
        pass

    def read_power(self):
        return 10 # 10dBm

    # Setting the source
    def set_unit(self, source: str="dBm", sensor: str="Watt"):
        pass

    def set_wavelength(self, wavelength: float):
        pass

    def switch_laser_state(self, status: bool):
        pass

    def set_power(self, power: float):
        pass

    # Setting source sweep parameters
    def set_sweep_mode(self, mode: str="STEP"): # STEP, MAN, CONT
        pass

    def set_sweep_start_stop(self, start: float, stop: float):
        pass

    def set_sweep_state(self, state: int): # 0 - stop, 1 - start, 2 - pause, 3 - continue
        pass
    
    def set_sweep_step(self, width: float):
        pass


class DummyPowerSupply:

    def __init__(self, rm, addr):
        pass

    def setup(self):
        pass

    def set_volt(self, volt: float):
        pass
    
    def set_current(self, curr: float):
        pass

    def set_params(self, volt: float, curr: float):
        pass

    def read_params(self): # read back (voltage, current)
        return (0, 0)

    def read_current(self):
        return 0
    
    def read_voltage(self):
        return 0
    
    def set_output_status(self, status: bool):
        pass

    def close(self):
        pass


class DummyILME:

    def __init__(self):
        pass

    def activate(self):
        pass
    
    def deactivate(self):
        pass

    def sweep_params(self, start: float=1540, stop: float=1575, step: float=5, power: float=10):
        pass

    def set_num_of_scans(self, num: int=1):
        pass

    def quit(self):
        pass

    def start_meas(self):
        pass

    def stop_meas(self):
        pass

    def get_no_channels(self):
        return 1

    def get_result(self, length: int=0):

        wavelength = (1, 2, 3, 4 ,5, 6, 7, 8, 9, 10)
        data = pd.DataFrame()
        data[f"CH1 - {length}"] = wavelength*2
        return wavelength, data

    def validate_settings(self):
        pass

