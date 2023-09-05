from pyoctal.util.file_operations import get_dataframe_from_excel, export_to_excel
import pandas as pd

fp = "./results/Chip_3/Si_iloss_data.xlsx"
sheet = "Si Waveguide"
df = get_dataframe_from_excel(filepath=fp, sheet_names=(sheet,))

df = df[sheet]
wavelength = df.loc[:,"Wavelength"]*1e+09

# df = df.apply(lambda x: -x)
df["Wavelength"] = wavelength

export_to_excel(data=df, sheet_names=(sheet,), folder="./results/Chip_3/", fname="Si_iloss_data.xlsx")
