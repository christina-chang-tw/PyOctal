
from lib.instruments import DummyILME

def test_import():
    ilme = DummyILME()
    assert type(ilme) == DummyILME

if __name__ == "__main__":
    test_import()