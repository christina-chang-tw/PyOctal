import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


filenames = ["ring1.5v_max_with_heater.csv","ring1.5v_min_with_heater.csv"]
folder = r"C:\Users\Lab2052\Desktop\Users\Christina\2024-5-07\s4_2_ramzi_ring_g200_3"
files = Path(folder).rglob("*.csv")

for file in files:
    df = pd.read_csv(file)

    plt.plot(df["Voltage [V]"]*df["Current [A]"], df["Power [W]"], label=file)

plt.legend()
plt.show()