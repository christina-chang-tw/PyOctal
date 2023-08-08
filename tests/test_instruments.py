
from lib.instruments import (
    AgilentE3640A
)

def test_E3640A():
    addr = "GPIB0::4::INSTR"
    volt = 3
    curr = 1
    instr = AgilentE3640A(addr=addr)
    instr.setup()

    assert instr.get_output_state() == 1
    instr.set_params(volt=volt, curr=curr)
    val = instr.get_params()

    assert val[0] == volt and val[1] == curr
    instr.set_output_state(0)

if __name__ == "__main__":
    test_E3640A()