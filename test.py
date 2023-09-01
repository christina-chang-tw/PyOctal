import pandas as pd

config_info = {
            "Wavelength start [nm]" : 1,
            "Wavelength stop [nm]"  : 2,
            "Wavelength step [nm]"  : 3,
            "Sweep rate [nm/s]"     : 4,
            "Output power [dBn]"    : 5,
        }

for key, val in config_info.items():
    print(f"{key:22} : {val}")


for i in range(0, 10):
    a = i

print(a)