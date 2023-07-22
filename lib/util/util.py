""" 
This file contains all sorts of functions
that are used but do not belong to a specific category
"""

import inspect
import sys
import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def get_func_name():
    return inspect.stack()[1].function

def wait_for_next_meas(i, total):
    print("\r")
    input("%s/%s : Press ENTER to continue" % (i, total))


def version_check():
    MIN_PYTHON = (3, 6)
    CUR_PYTHON = (sys.version_info.major, sys.version_info.minor)
    
    if sys.version_info <= MIN_PYTHON:
        sys.exit("Python %s.%s or later is required. Current version: Python %s.%s\n" % (MIN_PYTHON + CUR_PYTHON))

def get_gpib_full_addr(num: int=0):
    return f"GPIB::{num}::INSTR"

def get_config_dirpath():
    return f'{os.getcwd()}/config'

def get_result_dirpath(folder):
    return f'{os.getcwd()}/results/{folder}'

def package_info(info: dict):
    return pd.DataFrame(info.items(), columns=['Params', 'Value'])

def create_folder(folder: str="XXX"):
    try:
        path = f'{get_result_dirpath(folder)}'
        if not os.path.isdir(path):
            os.mkdir(path)
    except:
        sys.exit("Folder does not exist")
