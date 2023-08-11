from octal.base import BaseInstrument

class AgilentDSO8000(BaseInstrument):
    """ 
    Agilent DSO8000 Oscilloscopes VISA Library. 
    
    Parameters
    ----------
    addr: str
        The address of the instrument
    """

    def __init__(self, addr: str):
        super().__init__(rsc_addr=addr)

    def get_mag(self, chan: int) -> float:
        return self.query_float(f"measure:vamplitude? channel{chan}")
    