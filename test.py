import matplotlib.pyplot as plt

import pandas as pd

pd.read_csv('DCSweep.csv').plot(x='Voltage [V]', y='Power [W]')
plt.show()