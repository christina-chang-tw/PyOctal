""" Photonics Application Suite (PAS) Interface """

import math
import time
from typing import Tuple, List
from pathlib import Path
from os import makedirs

import numpy as np
import win32com.client

class BasePAS:
    """
    A base Photonics Application Suite class.
    
    This base object is put in here to ensure that people can use other instruments
    even though they are not using Windows OS

    Parameters
    ----------
    server_addr: str
        The address of the software
    """
    def __init__(self, server_addr: str, config: dict=None, config_path: Path=None):
        # connect to Engine Manager
        self.engine_mgr = win32com.client.Dispatch(server_addr)
        # List all engines running
        self.engine_ids = self.engine_mgr.EngineIDs
        self.connect(config_path)

    def connect(self, config: dict, config_path: Path):
        """ Connect to the engine. """
        # always connect to the first engine
        if self.engine_ids:
            self.engine = self.engine_mgr.OpenEngine(self.engine_ids[0])
            if config:
                self.engine.WavelengthStart = config.get("start", 0)*1e-09
                self.engine.WavelengthStop = config.get("stop", 0)*1e-09
                self.engine.WavelengthStep = config.get("step", 0)*1e-012
                self.engine.TLSPower = pow(10, (config.get("power", 0)/10))*1e-03
                self.engine.NumberOfScans = pow(10, (config.get("number of scans", 0)/10))*1e-03
                # self.engine.PWMRanges = pow(10, (config.get("power range", 0)/10))*1e-03
                self.engine.RangeDecrement = pow(10, (config.get("power decrement", 0)/10))*1e-03
                self.engine.SweepRate = config.get("sweep rate", -1)
                
                
        else:
            self.engine = self.engine_mgr.NewEngine()
            print(config_path)
            if config_path:
                self.load_configuration(config_path.absolute())
        
            self.activate()
            activating = 0
            start = time.time()

            # Check engine activation status
            while activating == 0:
                time.sleep(0.5) 
                activating = self.engine_state()
                if time.time() - start > 30:
                    raise TimeoutError("Timeout error: check devices connection")

    def activate(self):
        """ Active the engine. """
        self.engine.Activate()

    def deactivate(self):
        """ Active the deactivate. """
        self.engine.DeActivate()

    def engine_state(self):
        """ Check the engine state. """
        return self.engine.Active

    def quit(self):
        """ Quit the engine. """
        self.deactivate()
        self.engine_mgr.DeleteEngine(self.engine)

    def validate_settings(self):
        """ Validate the settings. """
        self.engine.ValidateSettings()

    def get_configuration(self):
        """ Virtually save the configuration into xml format. """
        return self.engine.Configuration

    def load_configuration(self, config):
        """ Load configuration. """
        self.engine.Configuration = config

    def __get_name(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return f"Photonics Application Suite: {self.__get_name()} "

    def __repr__(self) -> str:
        return f"{self.__get_name()}()"

    def __enter__(self):
        return self

class KeysightILME(BasePAS):
    """
    Keysight Insertion Loss Measurement Engine Win32com Library.

    This can control Agilent 8163B.
    """

    def __init__(self, *args, **kwargs):
        self.no_channels = 1
        server_addr = "AgServerIL.EngineMgr"
        super().__init__(server_addr=server_addr, *args, **kwargs)


    def sweep_params(self, start: float=1540, stop: float=1575, step: float=5, power: float=10):
        """ Set sweep parameters. """
        self.wavelength_start = start
        self.wavelength_stop = stop
        self.wavelength_step = step
        self.tls_power = power

    def get_dpts(self) -> int:
        """ Get the total wavelength datapoints. """
        return (self.wavelength_stop - self.wavelength_start)/(self.wavelength_step*1e-3) + 1

    @property
    def wavelength_start(self) -> float:
        """ Get the start wavelength in nm. """
        return self.engine.WavelengthStart*1e+09
    @wavelength_start.setter
    def wavelength_start(self, wavelength: float):
        """ Set the start wavelength in nm. """
        self.engine.WavelengthStart = wavelength*1e-09

    @property
    def wavelength_stop(self) -> float:
        """ Get the stop wavelength in nm. """
        return self.engine.WavelengthStop*1e+09
    @wavelength_stop.setter
    def wavelength_stop(self, wavelength: float):
        """ Set the stop wavelength in nm. """
        self.engine.WavelengthStop = wavelength*1e-09

    @property
    def wavelength_step(self) -> float:
        """ Get the step wavelength in pm. """
        return self.engine.WavelengthStep*1e+012
    @wavelength_step.setter
    def wavelength_step(self, step: float):
        """ Set the step wavelength in pm. """
        self.engine.WavelengthStep = step*1e-012

    @property
    def sweep_rate(self) -> float:
        """ Get the sweep rate in nm/s. """
        speed = self.engine.SweepRate
        if speed == -1:
            return "AUTO"
        return speed
    @sweep_rate.setter
    def sweep_rate(self, rate: float):
        """ Set the sweep rate in nm/s. """
        self.engine.SweepRate = rate

        
    @property
    def tls_output_port(self):
        return self.engine.TLSOutputPort
    
    @tls_output_port.setter
    def tls_output_port(self, port: int):
        self.engine.TLSOutputPort = port


    @property
    def tls_power(self) -> float:
        """ Get the laser power in dBm. """
        return 10*math.log10(self.engine.TLSPower/1e-03)
    @tls_power.setter
    def tls_power(self, power: float):
        """ Set the laser power in dBm. """
        self.engine.TLSPower = pow(10, (power/10))*1e-03

    @property
    def num_of_scans(self) -> int:
        """ Get number of scans. """
        return self.engine.NumberOfScans
    @num_of_scans.setter
    def num_of_scans(self, scan: int):
        """ Set number of scans. """
        self.engine.NumberOfScans = scan

    @property
    def range_decrement(self):
        return self.engine.RangeDecrement
    
    @range_decrement.setter
    def range_decrement(self, decrement: int):
        self.engine.RangeDecrement = decrement

    @property
    def measurement_result(self):
        return self.engine.MeasurementResult

    @property
    def pwm_ranges(self):
        return self.engine.PWMRanges

    @property
    def pwm_sensitivity(self):
        return self.engine.PWMSensitivity
    
    @property
    def zero_pwm_channels(self):
        return self.engine.ZeroPWMChannels

    
    
    @property
    def busy(self):
        return self.engine.Busy
    
    def tls_zeroing(self):
        """ Zero the TLS. """
        self.engine.ZeroTLS()

    def start_meas(self):
        """ Start one-shot measurement. """
        self.engine.StartMeasurement()

    def stop_meas(self):
        """ Stop a measurement. """
        self.engine.StopMeasurement()

    def get_result(self) -> Tuple[List, Tuple]:
        """ 
        Obtain result after the measurement.
        
        Parameter
        ---------
        col_name: str
            Column name 
        """

        # Wait for the sweep to finish
        while busy is True:
            time.sleep(0.1)
            busy = self.engine.Busy

        IOMRFile = self.engine.MeasurementResult
        IOMRGraph = IOMRFile.Graph("RXTXAvgIL")
        data_per_curve = IOMRGraph.dataPerCurve

        # Need to check if the channel number is always 1
        ydata = IOMRGraph.YData
    
        return self.get_wavelength(IOMRGraph, data_per_curve), ydata, IOMRFile

    @staticmethod
    def get_wavelength(IOMRGraph, data_per_curve) -> Tuple:
        """ Get all wavelength datapoints from a measurement. """
        xstart = IOMRGraph.xStart
        xstep = IOMRGraph.xStep
        xdata = [xstart + i * xstep for i in range(data_per_curve)]
        return tuple(np.divide(xdata, 1e-9))


def export_to_omr(data, filename: Path):
    """ Export the data to an OMR file. """
    makedirs(filename.parent, exist_ok=True)
    data.Write(filename.absolute())
