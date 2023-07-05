from lib.metadata import *

import openpyxl
import os.path
import pandas as pd
import csv

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TABLE_START_ROW = 10

def create_folder(path):
    try:
        if not os.path.isdir(path):
            os.mkdir(path)
        return
    except: NotADirectoryError
    print("Cannot open or create a folder")

def write_info():
    info = {
        'Name' : ['Christina'],
        'Age'  : [18],
        'University' : ['UoS'],
    }
    return pd.DataFrame(info).transpose()
    

def create_dataframe(path):
    if os.path.isfile(path):
        return _import_csv(path)
    return pd.DataFrame()


def _import_csv(path):
    df = pd.read_csv(path, sep='\t', encoding='utf-8')
    return df


def delete_file(path):
    try:
        os.remove(path)
    except: FileNotFoundError
    print("File is not found")


def export_csv(path, lists_of_dfs):
    with open(path, 'a') as f:
        for df in lists_of_dfs:
            df.to_csv(f, index=False)
            f.write('\n')


if __name__ == "__main__":
    name = "/test.csv"
    title = "insertion loss"
    folder_name = "/test/"
    
    folder = DIR_PATH + folder_name
    fpath = DIR_PATH + folder_name + "/test/"
    create_folder(folder)

    data = pd.DataFrame({"hello": [1, 2, 3], "bpn" : [4,5,6]})
    df = create_dataframe(folder)
    info = write_info()
    export_csv(folder, [info, data])

