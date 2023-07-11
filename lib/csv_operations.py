""" Functions related to CSV operations """

import os.path
import pandas as pd

def _dir_path():
    return os.getcwd() + "\\results\\"

def _get_dataframe(path: str, fname: str):
    path = path + fname
    if os.path.isfile(path) and os.stat(path).st_size != 0:
        return pd.read_csv(path, encoding='utf-8')
    return pd.DataFrame()


def create_folder(folder: str="XXX\\"):
    try:
        path = _dir_path() + folder    
        if not os.path.isdir(path):
            os.mkdir(path)
    except:
        print("Folder does not exist")

def package_info(info: dict):
    return pd.DataFrame(info.items(), columns=['Params', 'Value'])
    

def package_result(dataframe: pd.DataFrame, data, name: str="NaN"):
    dataframe[name] = data
    return dataframe

def export_csv(data: pd.DataFrame, folder: str="XXX/", fname: str="XXX"):
    path_to_file = f"{_dir_path()}{folder}/{fname}.csv"
    print(path_to_file)

    with open(path_to_file, 'w', encoding='utf-8') as f:
        data.to_csv(f, index=False)

if __name__ == "__main__":
    create_folder("XXX/")

