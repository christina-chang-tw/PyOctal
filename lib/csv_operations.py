import os.path
import pandas as pd

def _dir_path():
    return os.getcwd() + "/test/"

def _create_folder(path: str):
    try:
        if not os.path.isdir(path):
            os.mkdir(path)
        return
    except:
        yield NotADirectoryError()


def _get_dataframe(path: str, fname: str):
    path = path + fname
    if os.path.isfile(path) and os.stat(path).st_size != 0:
        return pd.read_csv(path, encoding='utf-8')
    return pd.DataFrame()


def df_initiate(folder: str="XXX", fname: str="XXX"):
    path = __dir_path() + folder
    fname = f'{fname}.csv'

    _create_folder(path=path)
    return _get_dataframe(path=path, fname=fname)

def package_info(info: dict):
    return pd.DataFrame(info.items(), columns=['Params', 'Value'])
    

def package_result(dataframe: pd.DataFrame, data, name: str="NaN"):
    dataframe[name] = data
    return dataframe

def export_csv(data: pd.DataFrame, folder: str="XXX", fname: str="XXX"):
    path = __dir_path() + folder
    fname = f'{fname}.csv'

    path_to_file = path + fname
    with open(path_to_file, 'w', encoding='utf-8') as f:
        data.to_csv(f, index=False)



