import pyvisa


from pyoctal.instruments import FiberlabsAMP

rm = pyvisa.ResourceManager()
amp = FiberlabsAMP(addr="GPIB0::1::INSTR", rm=rm)

print(amp.set_power(1,1e-03))

a = 1050
b = 1048

c = a % b
print(c)