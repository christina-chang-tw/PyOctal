""" 
Functions related to CSV or Excel operations 
"""
import pandas as pd
from typing import Union
from os import makedirs
from os.path import dirname

def export_to_csv(data: Union[pd.DataFrame, pd.Series], filename: str):
    folder = dirname(filename)
    makedirs(folder, exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as file:
        data.to_csv(file, index=False)


def export_to_excel(data: Union[pd.DataFrame, list, tuple], filename: str, sheet_names: Union[tuple, list]):

    folder = dirname(filename)
    makedirs(folder, exist_ok=True)

    with pd.ExcelWriter(filename) as writer:
        if isinstance(data, pd.DataFrame):
            data.to_excel(writer, sheet_name=f"{sheet_names[0]}", index=False)
        elif isinstance(data, Union[list, tuple]):
            for i, df in enumerate(data):
                df.to_excel(writer, sheet_name=f"{sheet_names[i]}", index=False)
