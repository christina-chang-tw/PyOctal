""" Photonics Application Suite (PAS) Interface """
from lib.base import BasePAS

import time
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class KeysightILME(BasePAS):
    """
    Keysight Insertion Loss Measurement Engine Win32com Library
    """

    def __init__(self):
        self.no_channels = 1
        server_addr = "AgServerIL.EngineMgr"
        super().__init__(server_addr=server_addr)


    def sweep_params(self, start: float=1540, stop: float=1575, step: float=5, power: float=10):
        """ Setting sweep parameters """
        self.engine.WavelengthStart = start * 1e-09
        self.engine.WavelengthStop = stop * 1e-09
        self.engine.WavelengthStep = step * 1e-12 # 0.3 x sweep rate [nm/s] = step size [pm]
        self.engine.TLSPower = pow(10, (power/10)) * 1e-03

    def set_num_of_scans(self, num: int=1):
        self.engine.NumberOfScans = num

    def start_meas(self):
        self.engine.StartMeasurement()

    def stop_meas(self):
        self.engine.StopMeasurement()

    def get_no_channels(self):
        return self.no_channels  

    def get_result(self, name: int=0):
        data = pd.DataFrame()

        busy = True
        while busy == True:
            time.sleep(0.1)
            busy = self.engine.Busy
        
        IOMRFile = self.engine.MeasurementResult
        IOMRGraph = IOMRFile.Graph("RXTXAvgIL")
        data_per_curve = IOMRGraph.dataPerCurve
        no_channels = IOMRGraph.noChannels
        self.no_channels = no_channels
        ydata = IOMRGraph.YData
        ycurve = [tuple(ydata[i*data_per_curve:(i+1)*data_per_curve]) for i in range(no_channels)]
        for i in range(no_channels):
            data[f"CH{i} - {name}"] = ycurve[i]
        IOMRFile.release()
        
        return self.get_wavelength(IOMRGraph, data_per_curve), data
    
    @staticmethod
    def get_wavelength(IOMRGraph, data_per_curve):
        xstart = IOMRGraph.xStart
        xstep = IOMRGraph.xStep
        xdata = [xstart + i * xstep for i in range(data_per_curve)]
        return tuple(np.divide(xdata, 1e-9))
    
    @staticmethod
    def export_file(results, fname):
        results.Write(fname)