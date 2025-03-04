from pyvisa import ResourceManager

from pyoctal.instruments.base import BaseInstrument

class Keithley6487(BaseInstrument):
    """
    Keithley 6487 Picoammeter VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """

    def __init__(self, rm: ResourceManager):
        super().__init__(rm=rm)

    def initiate(self):
        """ Initiate a measurement. """
        self.write("initiate")

    def measure(self, var: str) -> str:
        """ Measure the specified type. """
        self.value_check(var, ("curr", "volt"))
        return self.query(f"measure:{var}?")

    def read(self) -> str:
        """ Initiate and read a measurement. """
        return self.query("read?")

    ## Detector Commands ######################################
    def set_detect_mode(self, mode: str="current"):
        """ Set the detector mode. """
        self.value_check(mode.lower(), ("curr",))
        self.write(f"sense:function {mode}")

    def set_detect_autorange(self, state: bool):
        """ Set the detector current autorange. """
        self.write(f"sense:current:auto {state}")

    def set_detect_curr_range(self, crange: float):
        """ Set the detector current range. """
        self.value_check(crange, (-0.021, 0.021))
        self.write(f"sense:current:range {crange}")

    def set_detect_ohms_state(self, state: bool):
        """ Set the detector damping state. """
        self.write(f"sense:damping:ohms:state {state}")

    def get_detect_data(self):
        """ Get the detector data. """
        return self.query("sense:data?")


    ## Laser Commands ######################################
    def set_laser_state(self, state: bool):
        """ Set the laser output state. """
        self.write(f"source:voltage:state {state}")

    def set_laser_range(self, r: int):
        """ Set the laser voltage range. """
        self.value_check(r, (10, 50, 500))
        self.write(f"source:voltage:range {r}")
                
    def set_laser_volt(self, volt: float):
        """ Set the laser output voltage. """
        self.value_check(volt, (-500, 500))
        self.write(f"source:voltage:level {volt}")

    def set_laser_ilim(self, curr_lim: float):
        """ Set the laser current limit. """
        self.value_check(curr_lim, (-500, 500))
        self.write(f"source:voltage:ilimit {curr_lim}")

    def get_laser_volt(self) -> float:
        """ Get the laser voltage. """
        return self.query_float("source:voltage:level?")
    


    ## System Commands ######################################
    def set_sys_zch_state(self, state: bool):
        self.write(f"system:zcheck:state {state}")

    def set_sys_zcor_state(self, state: bool):
        self.write(f"system:zcorrect:state {state}")

    def set_sys_zcor_acq(self):
        self.write("system:zcorrect:acquire")


    ## Measure Commands ######################################
    def meas_curr(self) -> float:
        """ Measure current. """
        data = self.read() # Trigger and return one reading.
        return float(data.split(",")[0][:-1])
    
    def meas_resistance(self) -> float:
        """ Measure resistance. """
        data = self.read() # Trigger and return one reading.
        return float(data.split(",")[0][:-1].strip('OHM'))

    def meas_curr_raw(self) -> float:
        """ Measure raw current data. """
        data = self.get_detect_data() # Trigger and return one reading.
        return float(data.split(",")[1])

    def meas_volt(self) -> float:
        """ Measure voltage. """
        data = self.measure(var="volt")
        return float(data.split(",")[0])
    

    def meas_curr_zch(self) -> float:
        self.reset()
        self.set_sys_zch_state(1) # Enable zero check.
        self.set_detect_curr_range(crange=2e-09) # Select the 2nA range
        self.initiate() # Trigger reading to be used as zero correction.
        self.set_sys_zcor_acq() # Use last reading taken as zero correct value.
        self.set_sys_zcor_state(1) # Perform zero correction.
        self.set_detect_autorange(1) # Enable auto range.
        self.set_sys_zcor_state(0) # Perform zero correction.
        self.set_sys_zch_state(0) # Disable zero check.

        data = self.read() # Trigger and return one reading.
        return float(data.split(",")[1])
    
		
    def meas_curr_zch_ohm(self) -> float:
        self.reset()
        self.set_sys_zch_state(1) # Enable zero check.
        self.set_detect_curr_range(crange=2e-09) # Select the 2nA range
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



def main():
    instr = Keithley6487("GPIB0::22::INSTR")
    instr.set_laser_volt(5)


if __name__ == "__main__":
    main()