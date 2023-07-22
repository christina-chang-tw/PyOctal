import lib.util.file_operations as file_operations
import pandas as pd
import os

def test_excel_operation():
    dir_path = f'{os.getcwd()}/tests'
    fname = "excel"
    sheet_names = ("data 1", "data 2")

    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    data1 = [0, 1, 2, 3, 4]
    data2 = [5, 6, 7, 8, 9]

    df1["data 1"] = data1
    df2["data 2"] = data2


    file_operations.export_to_excel(data=[df1, df2], sheet_names=sheet_names, path=dir_path, fname=fname)
    df = file_operations.get_dataframe_from_excel(path=dir_path, fname=fname, sheet_names=sheet_names)
    print(df)

    assert df["data 1"].equals(df1)
    assert df["data 2"].equals(df2)
    
