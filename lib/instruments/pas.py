""" Photonics Application Suite (PAS) Interface """

from lib.csv_operations import export_csv

import win32com.client as win32
import time
import numpy as np
import pandas as pd

def release(obj):
    obj.release

class ILME:
    """
    Instrument: Insertion Loss Measurement Engine
    
    Remote control the ILME programme to run tests
    ** Not tested **
    """

    def __init__(self):
        self.engine_mgr = win32.gencache.EnsureDispatch('AgServerIL.EngineMgr')
        self.engine = self.engine_mgr.NewEngine()
        EngineIDs = self.engine_mgr.EngineIDs
        self.engine = self.engine_mgr.OpenEngine(EngineIDs[0])
        self.deactivate()

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
        self.enginer_mgr.DeleteEngine(self.engine)
        self.enginer_mgr.Release()

    def start_meas(self):
        self.engine.StartMeasurement()

    def stop_meas(self):
        self.engine.StopMeasurement()

    def process_status(self):
        return self.engine.EventMeasurementFinished # when an event is finished, the number will increase

    def get_result(self):
        busy = 1
        while busy == 1:
            time.sleep(0.1)
            busy = self.engine.Busy
        IOMRFile = self.engine.MeasurementResult
        IOMRGraph = IOMRFile.Graph("RXTXAvgIL")
        return self.get_wavelength(IOMRGraph), IOMRGraph.YData 
    
    @staticmethod
    def get_wavelength(IOMRGraph):
        XStart = IOMRGraph.xStart
        XStep = IOMRGraph.xStep
        dataPerCurve = IOMRGraph.dataPerCurve
        XData = [XStart + i * XStep for i in range(dataPerCurve)]   
        return tuple(np.divide(XData, 1e-9))

    @staticmethod
    def validate_settings(dev):
        dev.ValidateSettings()

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
