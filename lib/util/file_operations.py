""" 
Functions related to CSV or Excel operations 
"""

from lib.util.util import get_result_dirpath

import pandas as pd
import logging
from typing import Union
import os.path
import sys

logger = logging.getLogger(__name__)


def get_dataframe_from_csv(path: str, fname: str,):
    path_to_file = f'{path}/{fname}.csv'

    if os.path.isfile(path_to_file) and os.stat(path_to_file).st_size != 0:
        return pd.read_csv(path_to_file, encoding='utf-8')
    sys.exit("File does not exist")


def get_dataframe_from_excel(path: str, fname: str, sheet_names: Union[tuple, list]):
    path_to_file = f'{path}/{fname}.xlsx'

    if os.path.isfile(path_to_file) and os.stat(path_to_file).st_size != 0:
        data = dict()
        xl = pd.ExcelFile(path_to_file)
        data = {name: xl.parse(sheet_name=name) for name in sheet_names if name != "Overview"}
        if "Overview" in xl.sheet_names:
            info = xl.parse(sheet_name="Overview")
            return data, info
        return data
    sys.exit("Folder does not exist")



def export_to_csv(data: pd.DataFrame, path: str=get_result_dirpath("XXX"), fname: str="XXX"):
    path_to_file = f"{path}/{fname}.csv"

    with open(path_to_file, 'w', encoding='utf-8') as f:
        data.to_csv(f, index=False)


def export_to_excel(data: Union[pd.DataFrame, list, tuple], sheet_names: Union[tuple, list]=["sheet"], path: str=get_result_dirpath("XXX"), fname: str="XXX"):
    path_to_file = f"{path}/{fname}.xlsx"

    with pd.ExcelWriter(path_to_file) as writer:
        if isinstance(data, pd.DataFrame):
            data.to_excel(writer, sheet_name=f"{sheet_names[0]}", index=False)
        elif isinstance(data, Union[list, tuple]):
            [df.to_excel(writer, sheet_name=f"{sheet_names[i]}", index=False) for i, df in enumerate(data)]

