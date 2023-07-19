""" Functions related to CSV operations """
import pandas as pd

import logging
from typing import Union
import os.path

logger = logging.getLogger(__name__)


def get_ddir_path(folder):
    return f'{os.getcwd()}/results/{folder}'


def create_folder(folder: str="XXX"):
    try:
        path = f'{get_ddir_path(folder)}'
        if not os.path.isdir(path):
            os.mkdir(path)
    except:
        logger.error("Folder does not exist")


def get_dataframe_from_csv(dir: str, fname: str,):
    path_to_file = f'{dir}/{fname}.csv'

    if os.path.isfile(path_to_file) and os.stat(path_to_file).st_size != 0:
        return pd.read_csv(path_to_file, encoding='utf-8')
    logger.error("File does not exist")


def get_dataframe_from_excel(dir: str, fname: str, sheet_names: Union[tuple, list]):
    path_to_file = f'{dir}/{fname}.xlsx'

    if os.path.isfile(path_to_file) and os.stat(path_to_file).st_size != 0:
        data = dict()
        xl = pd.ExcelFile(path_to_file)
        info = xl.parse(sheet_name="Overview")
        data = {name: xl.parse(sheet_name=name) for name in sheet_names if name != "Overview"}
        return data, info

    logger.error("File does not exist")


def package_info(info: dict):
    return pd.DataFrame(info.items(), columns=['Params', 'Value'])


def export_to_csv(data: pd.DataFrame, path: str=get_ddir_path("XXX"), fname: str="XXX"):
    path_to_file = f"{path}/{fname}.csv"

    with open(path_to_file, 'w', encoding='utf-8') as f:
        data.to_csv(f, index=False)


def export_to_excel(data: Union[pd.DataFrame, list, tuple], path: str=get_ddir_path("XXX"), fname: str="XXX"):
    path_to_file = f"{path}/{fname}.xlsx"

    with pd.ExcelWriter(path_to_file) as writer:
        if isinstance(data, pd.DataFrame):
            data.to_excel(writer, sheet_name=f"sheet", index=False)
        elif isinstance(data, Union[list, tuple]):
            [df.to_excel(writer, sheet_name=f"sheet_{i}", index=False) for i, df in enumerate(data)]

