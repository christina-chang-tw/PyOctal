from octal.base import BaseInstrument

class ThorlabsPM100(BaseInstrument):
    """
    Thorlabs Power Monitor PM100 VISA Library

    Parameters
    ----------
    addr: str
        The address of the instrument
    """

    def __init__(self, addr: str):
        super().__init__(rsc_addr=addr)
        self.write("data:encd asci")

    def read(self):
        # Read the PM power (as shown on the display)
        return self.query("read?")
    
    def meas_power(self) -> float:
        # Measure the PM power (as shown on the display)
        self.write("measure:power")
        return self.query_float("fetch?")

    def set_wav(self, wavelength: float):
        # Set the power monitor wavelength [nm]
        self.write(f"sense:correction:wavelength {wavelength}")

    def set_avg_count(self, count: float):
        self.write(f"sense:average:count {count}")

    def set_curr_autorange_state(self, state: bool):
        self.write(f"current:range:auto {state}")

    def set_curr_reference(self, ref: float):
        self.write(f"current:reference {ref}")

    def set_pow_autorange_state(self, state: bool):
        self.write(f"power:range:auto {state}")

    def set_pow_reference(self, ref: float):
        self.write(f"power:reference {ref}")

    def set_volt_autorange_state(self, state: bool):
        self.write(f"voltage:range:auto {state}")

    def set_volt_reference(self, ref: float):
        self.write(f"voltage:reference {ref}")
