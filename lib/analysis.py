from lib.csv_operations import export_csv, create_folder
from lib.util import get_func_name

import numpy as np
import pandas as pd


def iloss(df, wavelengths, no_channels: int=1, chip_name: str="XXX"):
    """ 
    Extract the waveguide loss coefficient and insertion loss related to each wavelength to iloss_coeffs.csv file

    Variables
        df: data dataframe 
        wavelengths: the wavelengths that are stepped through
        chip_name: the name of the chip (must be distinguishable)
    """

    df = df.transpose() # transpose dataframe
    lengths = np.array([float(i.split(" - ")[1]) for i in df.index.tolist()])

    df_coeff = pd.DataFrame()
    df_coeff["lambda"] = wavelengths

    for i in range(0, len(df.columns)):
        for j in range(no_channels):
            fit = np.polyfit(lengths, df.iloc[:, i].to_numpy(), deg=1)
            df_coeff.loc[i, f"CH{j} - loss [db/um]"] = round(fit[0],5)
            df_coeff.loc[i, f"CH{j} - insertion loss [dB]"] = round(fit[1], 5)

    return df_coeff
   


if __name__ == "__main__":
    create_folder("XXX/")
    info = {1 : 4, 2 : 5, 3 : 6}

    df = pd.DataFrame(info.items(), columns=["10", "20"])

    iloss("XXX", df, [1, 2, 3])

