import lib.util.file_operations as file_operations
import pandas as pd
import os

def test_excel_operation():
    dir_path = f'{os.getcwd()}/tests'
    fname = "excel"

    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    data1 = [0, 1, 2, 3, 4]
    data2 = [5, 6, 7, 8, 9]

    df1["data 1"] = data1
    df2["data 2"] = data2

    file_operations.export_to_excel([df1, df2], dir_path, fname)
    df = file_operations.get_dataframe_from_excel(dir_path, fname)

    assert df[0].equals(df1)
    assert df[1].equals(df2)
    
