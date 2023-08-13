from pyoctal.base import BaseInstrument

class EXFOXTA50(BaseInstrument):
    """
    EXFOXTA 50 VISA Library.
    
    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """

    def __init__(self, addr: str, rm):
        super().__init__(rsc_addr=addr, rm=rm)

    @property
    def serial_no(self):
        return self.query("serial_number?")
    
    def set_freq(self, freq: float):
        """ Set frequency [THz]. """
        self.write(f"freq={freq}")

    def set_wavelength(self, wavelength: float):
        """ Set frequency [nm]. """
        self.write(f"lambda={wavelength}")

    def set_fwhm(self, fwhm: float):
        """ Set frequency [nm]. """
        self.write(f"fwhm={fwhm}")

    def get_freq(self) -> float:
        """ Get frequency [THz]. """
        return self.query_float("freq?")

    def get_fwhm(self) -> float:
        """ Get full-width half maximum frequency. """
        return self.query_float("fwhm?")
    
    def get_wavelength(self) -> float:
        """ Set laser output state. """
        return self.query_float("lambda?")
    
    def is_seq_running(self) -> bool:
        """ Check if a sequence is still being executed. """
        return self.query_bool("sequence_running?")
    
    def set_local(self):
        """ Switch to local control. """
        self.write("local")

