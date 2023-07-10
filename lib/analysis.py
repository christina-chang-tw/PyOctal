from lib.csv_operations import export_csv, create_folder
from lib.util import get_func_name

import numpy as np
import pandas as pd


def iloss(df, wavelengths, chip_name):

    df = df.transpose() # transpose dataframe
    x = np.array([float(i) for i in df.index.tolist()])

    df_coeff = pd.DataFrame(columns=["lambda", "loss [db/um]", "insertion loss [dB]"])
    df_coeff["lambda"] = wavelengths

    for i in range(0, len(df.columns)):
        fit = np.polyfit(x, df.iloc[:, i].to_numpy(), deg=1)
        df_coeff.loc[i, "loss [db/um]"] = round(fit[0],2)
        df_coeff.loc[i, "insertion loss [dB]"] = round(fit[1], 2)

    export_csv(df_coeff, chip_name, f'{get_func_name()}_coeffs')
        


if __name__ == "__main__":
    create_folder("XXX/")
    info = {1 : 4, 2 : 5, 3 : 6}

    df = pd.DataFrame(info.items(), columns=["10", "20"])

    iloss("XXX", df, [1, 2, 3])
    
