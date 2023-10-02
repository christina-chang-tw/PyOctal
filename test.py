import pyvisa


from pyoctal.instruments import FiberlabsAMP

rm = pyvisa.ResourceManager()
amp = FiberlabsAMP(addr="GPIB0::1::INSTR", rm=rm)

print(amp.set_curr(1,1035))

a = 1050
b = 1048

c = a % b
print(c)