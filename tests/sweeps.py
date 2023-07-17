from lib.sweeps.passive import ILossSweep
from lib.instruments.dummy import DummyILME

def test_iloss_sweeps():
    

    sweep = ILossSweep(DummyILME)

if __name__ == "__main__":
    test_iloss_sweeps()

