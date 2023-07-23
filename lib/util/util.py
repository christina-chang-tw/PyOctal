""" 
This file contains all sorts of functions
that are used but do not belong to a specific category
"""
from lib.error import *
from . import __platform__, __python_min_version__

import inspect
import sys
import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def platform_check():
    if sys.platform not in __platform__:
        raise EnvironmentError("Error code %s: %s. Current platform is %s" % (INCOMPATIBLE_OS_ERR, error_message[INCOMPATIBLE_OS_ERR], sys.platform))
    print("Using Windows OS platform...")


def version_check():
    MIN_PYTHON = __python_min_version__
    CUR_PYTHON = (sys.version_info.major, sys.version_info.minor)
    if sys.version_info <= MIN_PYTHON:
        raise ValueError("Error code %s: %s. Python %s.%s or later is required. Current version: Python %s.%s\n" % (PYTHON_VER_ERROR, error_message[PYTHON_VER_ERROR], MIN_PYTHON[0], MIN_PYTHON[1], CUR_PYTHON[0], CUR_PYTHON[1]))
    print("Using correct Python version...")

def get_func_name():
    return inspect.stack()[1].function

def wait_for_next_meas(i, total):
    print("\r")
    input("%s/%s : Press ENTER to continue" % (i, total))

def get_gpib_full_addr(num: int=0):
    return f"GPIB::{num}::INSTR"

def get_com_full_addr(num: int=0):
    return f"COM{num}"

def get_config_dirpath():
    return f'{os.getcwd()}/config'

def get_result_dirpath(folder):
    return f'{os.getcwd()}/results/{folder}'

def package_info(info: dict):
    return pd.DataFrame(info.items(), columns=['Params', 'Value'])

def create_folder(path: str="XXX"):
    try:
        if not os.path.isdir(path):
            os.mkdir(path)
    except:
        raise FileExistsError(f"Error code {FOLDER_NOT_EXIST_ERR}: {error_message[FOLDER_NOT_EXIST_ERR]}")
    
def delete_folder(path: str="XXX"):
    try:
        os.rmdir(path) 
    except:
        raise FileExistsError(f"Error code {FOLDER_NOT_EXIST_ERR}: {error_message[FOLDER_NOT_EXIST_ERR]}")
    
