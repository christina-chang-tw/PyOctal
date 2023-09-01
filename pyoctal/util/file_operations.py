""" 
Functions related to CSV or Excel operations 
"""
import pandas as pd
import os.path
from typing import Union

from pyoctal.error import FILE_NOT_EXIST_ERR, FILE_EMPTY_ERR, error_message
from pyoctal.util.util import create_folder


def get_dataframe_from_csv(filepath: str) -> pd.DataFrame:
    if not os.path.isfile(filepath):
        raise FileExistsError(f"Error code {FILE_NOT_EXIST_ERR}: {error_message[FILE_NOT_EXIST_ERR]}")
    elif os.stat(filepath).st_size == 0:
        raise ImportError(f"Error code {FILE_EMPTY_ERR}: {error_message[FILE_EMPTY_ERR]}")
    return pd.read_csv(filepath, encoding='utf-8')


def get_dataframe_from_excel(filepath: str, sheet_names: Union[tuple, list]) -> pd.DataFrame:
    if not os.path.isfile(filepath):
        raise FileExistsError(f"Error code {FILE_NOT_EXIST_ERR}: {error_message[FILE_NOT_EXIST_ERR]}")
    elif os.stat(filepath).st_size == 0:
        raise ImportError(f"Error code {FILE_EMPTY_ERR}: {error_message[FILE_EMPTY_ERR]}")

    xl = pd.ExcelFile(filepath)
    # make a dictionary of {sheet: sheetdata}
    data = {name: xl.parse(sheet_name=name) for name in sheet_names if name != "Overview"}
    return data


def export_to_csv(data: Union[pd.DataFrame, pd.Series], folder: str="./xxx", fname: str="xxx.csv"):
    create_folder(path=folder)
    path_to_file = f"{folder}/{fname}"

    with open(path_to_file, 'w', encoding='utf-8') as file:
        data.to_csv(file, index=False)


def export_to_excel(data: Union[pd.DataFrame, list, tuple], sheet_names: Union[tuple, list]=["sheet"], folder: str="./xxx", fname: str="xxx.xlsx"):
    create_folder(path=folder)
    path_to_file = f"{folder}/{fname}"

    with pd.ExcelWriter(path_to_file) as writer:
        if isinstance(data, pd.DataFrame):
            data.to_excel(writer, sheet_name=f"{sheet_names[0]}", index=False)
        elif isinstance(data, Union[list, tuple]):
            for i, df in enumerate(data):
                df.to_excel(writer, sheet_name=f"{sheet_names[i]}", index=False)
