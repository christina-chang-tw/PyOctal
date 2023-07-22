from lib.base import BaseSweeps
from lib.util.plot import RealTimePlot
from lib.util.util import get_result_dirpath
from lib.util.file_operations import export_to_csv

import time
import pandas as pd

class IVSweeps(BaseSweeps):

    def __init__(self, instr):
        super().__init__(instr=instr)
        self.display = RealTimePlot()

    def sweep(self, configs):
        v_start = configs["v_start"]
        v_stop = configs["v_stop"]
        step = configs["step"]

        df = pd.DataFrame
        voltage = []
        current = []
        
        self.instr.set_laser_state(1) # turn the laser on
    
        for volt in range(v_start, v_stop, step):
            self.instr.set_laser_volt(volt)
            time.sleep(0.01) # pause the plotting
            
            curr = self.instr.meas_curr()
            self.display.add(volt, curr)
            self.display.pause(0.001)

            voltage.append(volt)
            current.append(current)

        df["Voltage"] = voltage
        df["Current"] = current
        
        export_to_csv(data=df, path=get_result_dirpath(configs["folders"]), fname=configs["structure"])

        self.instr.set_laser_volt(0) 
        self.instr.set_laser_state(0) # turn laser off
        
        self.display.show() # show the plot




