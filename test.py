import pyvisa
import os
import time


from pyoctal.instruments import FiberlabsAMP

from pyoctal.instruments import KeysightILME
# rm = pyvisa.ResourceManager()
# amp = FiberlabsAMP(addr="GPIB0::1::INSTR", rm=rm)

# print(amp.set_curr(1,1035))

# a = 1050
# b = 1048

# c = a % b
# print(c)

ilme = KeysightILME()
ilme.activate()
ilme.start_meas()
busy = True

        # Wait for the sweep to finish
while busy == True:
    time.sleep(0.1)
    busy = ilme.busy
result = ilme.measurement_result

ilme.export_omr(result, "./test", "a.omr")