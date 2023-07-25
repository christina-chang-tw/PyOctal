from lib.base import BaseInstrument

class AgilentDSO8000(BaseInstrument):

    def __init__(self, addr):
        super().__init__(rsc_addr=addr)

    def get_mag(self, chan) -> float:
        return self.query_float(f"measure:vamplitude? channel{chan}")