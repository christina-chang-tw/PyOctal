""" Photonics Application Suite (PAS) Interface """

from lib.csv_operations import export_csv

import win32com.client
import time
import numpy as np
import pandas as pd


class ILME:
    """
    Instrument: Insertion Loss Measurement Engine
    
    Remote control the ILME programme to run tests
    ** Not tested **
    """

    def __init__(self):
        self.engine_mgr = win32com.client.Dispatch('AgServerIL.EngineMgr')
        self.engine = self.engine_mgr.NewEngine()
        self.activate()

        activating = 0
        while activating == 0:
            time.sleep(0.5) 
            activating = self.engine.Active

    def activate(self):
        self.engine.Activate()
    
    def deactivate(self):
        self.engine.DeActivate()

    def sweep_params(self, start: float=1540, stop: float=1575, step: float=5, power: float=10):
        """ Setting sweep parameters """
        self.engine.WavelengthStart = start * 1e-09
        self.engine.WavelengthStop = stop * 1e-09
        self.engine.WavelengthStep = step * 1e-12 # 0.3 x sweep rate [nm/s] = step size [pm]
        self.engine.TLSPower = pow(10, (power/10)) * 1e-03

    def set_num_of_scans(self, num: int=1):
        self.engine.NumberOfScans = num

    def quit(self):
        self.deactivate()
        self.engine_mgr.DeleteEngine(self.engine)
        self.engine_mgr.release()

    def start_meas(self):
        self.engine.StartMeasurement()

    def stop_meas(self):
        self.engine.StopMeasurement()

    def get_result(self):
        busy = 1
        while busy == 1:
            time.sleep(0.1)
            busy = self.engine.Busy
        IOMRFile = self.engine.MeasurementResult
        IOMRGraph = IOMRFile.Graph("RXTXAvgIL")
        data_per_curve = IOMRGraph.dataPerCurve
        no_channels = IOMRGraph.noChannels
        ydata = IOMRGraph.YData
        ycurve = [tuple(np.negative(ydata[i*data_per_curve:(i+1)*data_per_curve])) for i in range(no_channels)]
        return self._get_wavelength(IOMRGraph, data_per_curve), ycurve
    
    @staticmethod
    def _get_wavelength(IOMRGraph, data_per_curve):
        xstart = IOMRGraph.xStart
        xstep = IOMRGraph.xStep
        xdata = [xstart + i * xstep for i in range(data_per_curve)]
        return tuple(np.divide(xdata, 1e-9))

    def validate_settings(self):
        self.engine.ValidateSettings()

if __name__ == "__main__":
    engine = ILME()
    engine.activate()
    engine.sweep_params()
    engine.start_meas()

    x, y = engine.get_result()
    x = pd.DataFrame(x)
    y = pd.DataFrame(y)
    with open("./x.csv", 'w', encoding='utf-8') as f:
        x.to_csv(f, index=False)
    with open("./y.csv", 'w', encoding='utf-8') as f:
        y.to_csv(f, index=False)
