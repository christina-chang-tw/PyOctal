from lib.metadata import *
import os.path
import pandas as pd


DIR_PATH = os.getcwd() + "/test/"
TABLE_START_ROW = 10


def create_folder(path: str):
    try:
        if not os.path.isdir(path):
            os.mkdir(path)
        return
    except: NotADirectoryError
    print("Cannot open or create a folder")


def package_info(info: dict):
    return pd.DataFrame(info.items(), columns=['Params', 'Value'])
    

def get_dataframe(path: str, fname: str):
    path = path + fname
    if os.path.isfile(path) and os.stat(path).st_size != 0:
        return pd.read_csv(path, encoding='utf-8')
    return pd.DataFrame()


def package_result(dataframe: pd.DataFrame, data, name: str="NaN"):
    dataframe[name] = data
    return dataframe



def export_csv(path: str, fname: str, data: pd.DataFrame):
    path = path + fname
    with open(path, 'w', encoding='utf-8') as file:
        data.to_csv(file, index=False)



if __name__ == "__main__":
    name1 = "test.csv"
    name2 = "table.csv"
    title = "insertion loss"
    folder_name = f"/{CHIP_NAME}/"
    
    folder = DIR_PATH + folder_name
    create_folder(folder)

    info = {
    'Name' : 'Christina',
    'Age'  : 18,
    'University' : 'UoS',
    }

    df1 = get_dataframe(folder, name1)
    df2 = get_dataframe(folder, name2)
    info = package_info(info)
    df2 = package_result(df2, [1,2,3,4,5], "40nm")
    df2 = package_result(df2, [3,10,20,4,5], "10nm")

    print(df2)
    export_csv(folder, name1, info)
    export_csv(folder, name2, df2)

