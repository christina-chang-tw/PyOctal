""" 
Functions related to CSV or Excel operations 
"""
from typing import Union, List, Tuple
from os import makedirs
from pathlib import Path

import pandas as pd

def export_to_excel(data: Union[pd.DataFrame, List, Tuple],
                    filename: Path, sheet_names: Union[Tuple, List]):
    """
    Export data to an Excel file.

    Parameters
    ----------
    data: Union[pd.DataFrame, List, Tuple]
        Data to be exported
    filename: Path
        File name to be saved
    """
    makedirs(filename.parent, exist_ok=True)

    with pd.ExcelWriter(filename) as writer:
        if isinstance(data, pd.DataFrame):
            data.to_excel(writer, sheet_name=f"{sheet_names[0]}", index=False)
        elif isinstance(data, Union[List, Tuple]):
            for i, df in enumerate(data):
                df.to_excel(writer, sheet_name=f"{sheet_names[i]}", index=False)
