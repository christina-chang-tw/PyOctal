from pyoctal.base import BaseInstrument

class AgilentDSO8000(BaseInstrument):
    """ 
    Agilent DSO8000 Oscilloscopes VISA Library. 
    
    Parameters
    ----------
    addr: str
        The address of the instrument
    rm: str
        Argument for resource manager (for simualated device only)
    """

    def __init__(self, addr: str, rm: str=""):
        super().__init__(rsc_addr=addr, rm=rm)

    def get_mag(self, chan: int) -> float:
        """ Get the magnitude of a channel. """
        return self.query_float(f"measure:vamplitude? channel{chan}")
    