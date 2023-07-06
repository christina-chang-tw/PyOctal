import win32com.client as win32
import time


class PAL:
    def __init__(self):
        self.enginer_mgr = win32.gencache.EnsureDispatch('AgServerILPDL.EnginerMgr')
        self.engine = self.enginer_mgr.NewEngine
        
    def activate(self):
        self.engine.Activate
    
    def deactivate(self):
        self.engine.Deactivate

    def quit(self):
        self.engine.release
        self.enginer_mgr.release

    def start_meas(self):
        self.engine.StartMeasurement

    def get_result(self):
        while self.engine.Busy:
            time.sleep(1)
        return self.engine.MeasurementResult
    
    def release(obj):
        obj.release