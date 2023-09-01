""" Photonics Application Suite (PAS) Interface """
import win32com.client

import math
import time
import numpy as np
import pandas as pd
from typing import Tuple

class BasePAS(object):
    """
    A base Photonics Application Suite class.
    
    This base object is put in here to ensure that people can use other instruments
    even though they are not using Windows OS

    Parameters
    ----------
    server_addr: str
        The address of the software
    """
    def __init__(self, server_addr: str):
        # connect to Engine Manager
        self.engine_mgr = win32com.client.Dispatch(server_addr)
        # list all engines running
        self.engine_ids = self.engine_mgr.EngineIDs()
        self.connect()

    def connect(self):
        # always connect to the first engine
        self.engine = self.engine_mgr.OpenEngine(self.engine_ids(1))
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


class KeysightILME(BasePAS):
    """
    Keysight Insertion Loss Measurement Engine Win32com Library.

    This can control Agilent 8163B.
    """

    def __init__(self):
        self.no_channels = 1
        server_addr = "AgServerIL.EngineMgr"
        super().__init__(server_addr=server_addr)


    def sweep_params(self, start: float=1540, stop: float=1575, step: float=5, power: float=10):
        """ Set sweep parameters. """
        self.wavelength_start = start
        self.wavelength_stop = stop
        self.wavelength_step = step
        self.tls_power = power

    @property
    def wavelength_start(self) -> float:
        """ Get the start wavelength in nm. """
        return self.engine.WavelengthStart*10e+09
    @wavelength_start.setter
    def wavelength_start(self, wavelength: float):
        """ Set the start wavelength in nm. """
        self.engine.WavelengthStart = wavelength*10e-09

    @property
    def wavelength_stop(self) -> float:
        """ Get the stop wavelength in nm. """
        return self.engine.WavelengthStop*10e+09
    @wavelength_stop.setter
    def wavelength_stop(self, wavelength: float):
        """ Set the stop wavelength in nm. """
        self.engine.WavelengthStop = wavelength*10e-09

    @property
    def wavelength_step(self) -> float:
        """ Get the step wavelength in pm. """
        return self.engine.WavelengthStep*10e+012
    @wavelength_step.setter
    def wavelength_step(self, step: float):
        """ Set the step wavelength in pm. """
        self.engine.WavelengthStep = step*10e-012

    @property
    def sweep_rate(self) -> float:
        """ Get the sweep rate in nm/s. """
        return self.engine.SweepRate
    @sweep_rate.setter
    def sweep_rate(self, rate: float):
        """ Set the sweep rate in nm/s. """
        self.engine.SweepRate = rate

    @property
    def tls_power(self) -> float:
        """ Get the laser power in dBm. """
        return 10*math.log10(self.engine.TLSPower/10e-03)
    @tls_power.setter
    def tls_power(self, power: float):
        """ Set the laser power in dBm. """
        self.engine.TLSPower = pow(10, (power/10))*10e-03

    @property
    def num_of_scans(self) -> int:
        """ Get number of scans. """
        return self.engine.NumberOfScans
    @num_of_scans.setter
    def num_of_scans(self, scan: int):
        """ Set number of scans. """
        self.engine.NumberOfScans = scan

    def start_meas(self):
        """ Start one-shot measurement. """
        self.engine.StartMeasurement()

    def stop_meas(self):
        """ Stop a measurement. """
        self.engine.StopMeasurement()

    def get_result(self) -> Tuple[tuple, tuple]:
        """ 
        Obtain result after the measurement.
        
        Parameter
        ---------
        col_name: str
            Column name 
        """
        busy = True

        # Wait for the sweep to finish
        while busy == True:
            time.sleep(0.1)
            busy = self.engine.Busy
        
        IOMRFile = self.engine.MeasurementResult
        IOMRGraph = IOMRFile.Graph("RXTXAvgIL")
        data_per_curve = IOMRGraph.dataPerCurve
        no_channels = IOMRGraph.noChannels
        ydata = IOMRGraph.YData
        ycurve = [tuple(ydata[i*data_per_curve:(i+1)*data_per_curve]) for i in range(no_channels)]
        
        return self.get_wavelength(IOMRGraph, data_per_curve), ycurve
    
    @staticmethod
    def get_wavelength(IOMRGraph, data_per_curve) -> tuple:
        """ Get all wavelength datapoints from a measurement. """
        xstart = IOMRGraph.xStart
        xstep = IOMRGraph.xStep
        xdata = [xstart + i * xstep for i in range(data_per_curve)]
        return tuple(np.divide(xdata, 1e-9))
    
    @staticmethod
    def export_file(results, fname):
        results.FileSave(fname)