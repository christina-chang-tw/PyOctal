import win32com.client as win32
import time
import numpy as np
import pandas as pd


class PAL:
    def __init__(self):
        self.enginer_mgr = win32.gencache.EnsureDispatch('AgServerILPDL.EnginerMgr')
        self.engine = self.enginer_mgr.NewEngine
        self.tls = self.engine.GetTLSInterface(0)
        
    def activate(self):
        self.engine.Activate
    
    def deactivate(self):
        self.engine.Deactivate

    def sweep_params(self, start: float=1540, stop: float=1575, rate: float=5, power: float=10):
        self.tls.WavelengthStart = start
        self.tls.WavelengthStop = stop
        self.tls.SweepRate = rate # 0.3 x sweep rate [nm/s] = step size [pm]
        self.tls.TLSPower = power


    def quit(self):
        self.engine.release
        self.enginer_mgr.DeleteEngine(self.engine)
        self.enginer_mgr.release

    def start_meas(self):
        self.engine.StartMeasurement

    def stop_meas(self):
        self.engine.StopMeasurement

    def process_status(self):
        return self.engine.EventMeasurementFinished # when an event is finished, the number will increase

    def get_result(self):
        while self.engine.Busy:
            time.sleep(1)
        result = self.engine.MeasurementResult
        graph = result.Graph("TLS0_RXTXAvgIL")
        return graph, graph.YData
    
    def release(obj):
        obj.release

if __name__ == "__main__":
    engine = PAL()