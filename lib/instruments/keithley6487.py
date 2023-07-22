from lib.base import BaseInstrument

class Keithley6487(BaseInstrument):
    """
    Keithley 6487 Picoammeter VISA Library

    Parameters
    ----------
    addr: str
        The address of the instrument
    """

    def __init__(self, addr):
        super().__init__(rsc_addr=addr)

    def initiate(self):
        self.write("initiate")

    def measure(self, var: str):
        if var.lower() not in ("curr", "volt"):
            raise RuntimeError("Bad value")
        return self.query_float(f"measure:{var}?")

    def read(self):
        return self.query("read?")

    # Detector
    def set_detect_mode(self, mode: str="current"):
        if mode.lower() not in ("curr",):
            raise RuntimeError("Bad value")
        self.write(f"sense:function {mode}")

    def set_detect_autorange(self, state: bool=1):
        self.write(f"sense:current:auto {state}")

    def set_detect_curr_range(self, r: float):
        if not -0.021 <= r <= 0.021:
            raise RuntimeError("Bad value")
        self.write(f"sense:current:range {r}")

    def set_detect_ohms_state(self, state: bool=1):
        self.write(f"sense:damping:ohms:state {state}")

    def get_detect_data(self):
        return self.query("sense:data?")


    # Laser
    def set_laser_state(self, state: bool):
        self.write(f"source:voltage:state {state}")

    def set_laser_range(self, r: int):
        if r not in (10, 50, 500): # in V 
            raise RuntimeError("Bad value")
		self.write(f"source:voltage:range {r}")
                
    def set_laser_volt(self, volt: float=0):
        if not -500 <= range <= 500:
            raise RuntimeError("Bad value")
        self.write(f"source:voltage:level {volt}")

    def set_laser_ilim(self, curr_lim: float=2.5e-02):
        if not -500 <= curr_lim <= 500:
            raise RuntimeError("Bad value")
        self.write(f"source:voltage:ilimit {curr_lim}")

    def get_laser_volt(self):
        return self.query(f"source:voltage:level?")
    


    # System
    def set_sys_zch_state(self, state: bool=1):
        self.write(f"system:zcheck:state {state}")

    def set_sys_zcor_state(self, state: bool=1):
        self.write(f"system:zcorrect:state {state}")

    def set_sys_zcor_acq(self):
        self.write("system:zcorrect:acquire")


    def meas_curr_zch(self):
        self.reset()
        self.set_sys_zch_state(1) # Enable zero check.
        self.set_detect_curr_range(r=2e-09) # Select the 2nA range
        self.initiate() # Trigger reading to be used as zero correction.
        self.set_sys_zcor_acq() # Use last reading taken as zero correct value.
        self.set_sys_zcor_state(1) # Perform zero correction.
        self.set_detect_autorange(1) # Enable auto range.
        self.set_sys_zcor_state(0) # Perform zero correction.
        self.set_sys_zch_state(0) # Disable zero check.

        data = self.read() # Trigger and return one reading.
        return float(data.split(",")[1])
    
		
    def meas_curr_zch_ohm(self):
        self.reset()
        self.set_sys_zch_state(1) # Enable zero check.
        self.set_detect_curr_range(r=2e-09) # Select the 2nA range
        self.initiate() # Trigger reading to be used as zero correction.
        self.set_sys_zcor_acq() # Use last reading taken as zero correct value.
        self.set_sys_zcor_state(1) # Perform zero correction.
        self.set_detect_autorange(1) # Enable auto range.
        self.set_laser_range(r=10)
        self.set_laser_volt(volt=10)
        self.set_laser_ilim(curr_lim=2.5e-03)
        self.set_laser_state(1)
        self.set_sys_zch_state(0) # Disable zero check.
	
        data = self.read() # Trigger and return one reading.
        return float(data.split(",")[1].strip('OHM'))

    def meas_curr(self):
        data = self.read() # Trigger and return one reading.
        return float(data.split(",")[0][:-1])


    def meas_resistance(self):
        data = self.read() # Trigger and return one reading.
        return float(data.split(",")[0][:-1].strip('OHM'))
		

    def meas_curr_raw(self):
        data = self.get_detect_data() # Trigger and return one reading.
        return float(data.split(",")[1])

    def meas_volt(self):
        data = self.measure(var="volt")
        return float(data.split(",")[0])
