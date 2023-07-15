""" Functions related to CSV operations """

import os.path
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def get_ddir_path():
    return os.getcwd() + "/results"

def get_dataframe(path: str):
    if os.path.isfile(path) and os.stat(path).st_size != 0:
        return pd.read_csv(path, encoding='utf-8')
    logger.error("File does not exist")


def create_folder(folder: str="XXX"):
    try:
        path = f'{get_ddir_path()}/{folder}/'
        if not os.path.isdir(path):
            os.mkdir(path)
    except:
        logger.error("Folder does not exist")

def package_info(info: dict):
    return pd.DataFrame(info.items(), columns=['Params', 'Value'])

def export_csv(data: pd.DataFrame, folder: str="XXX/", fname: str="XXX"):
    path_to_file = f"{get_ddir_path()}/{folder}/{fname}.csv"

    with open(path_to_file, 'w', encoding='utf-8') as f:
        data.to_csv(f, index=False)

if __name__ == "__main__":
    create_folder("XXX/")

