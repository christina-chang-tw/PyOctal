from pyoctal.base import BaseInstrument

class EXFOXTA50(BaseInstrument):
    """
    EXFOXTA 50 VISA Library.
    
    Parameters
    ----------
    addr: str
        The address of the instrument
    """

    def __init__(self, addr: str):
        super().__init__(rsc_addr=addr)

    @property
    def serial_no(self):
        return self.query("serial_number?")
    
    def set_freq(self, freq: float):
        """ Set frequency in THz """
        self.write(f"freq={freq}")

    def set_lambda(self, wavelength: float):
        """ Set frequency in nm """
        self.write(f"lambda={wavelength}")

    def set_fwhm(self, fwhm: float):
        """ Set frequency in nm """
        self.write(f"fwhm={fwhm}")

    def get_freq(self) -> float:
        return self.query_float("freq?")

    def get_fwhm(self) -> float:
        return self.query_float("fwhm?")
    
    def get_lambda(self) -> float:
        return self.query_float("lambda?")
    
    def is_seq_running(self) -> bool:
        return self.query_bool("sequence_running?")
    
    def set_local(self):
        self.write("local")

