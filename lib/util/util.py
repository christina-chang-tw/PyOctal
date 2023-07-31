""" 
This file contains all sorts of functions
that are used but do not belong to a specific category
"""
from lib.error import *
from . import __python_min_version__, __platform__

import inspect
import sys
import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def platform_check():
    try:
        if sys.platform not in __platform__:
            raise SystemError("Error code %s: %s. Current platform is %s" % (INCOMPATIBLE_OS_ERR, error_message[INCOMPATIBLE_OS_ERR], sys.platform))
    except SystemError as error:
        raise error

def pyversion_check():
    try:
        MIN_PYTHON = __python_min_version__
        CUR_PYTHON = (sys.version_info.major, sys.version_info.minor)
        if sys.version_info <= MIN_PYTHON:
            raise SystemError("Error code %s: %s. Python %s.%s or later is required. Current version: Python %s.%s\n" % (PYTHON_VER_ERROR, error_message[PYTHON_VER_ERROR], MIN_PYTHON[0], MIN_PYTHON[1], CUR_PYTHON[0], CUR_PYTHON[1]))
    except SystemError as error:
        raise error

def get_func_name() -> str:
    return inspect.stack()[1].function

def wait_for_next_meas(i, total):
    print("\r")
    input("%s/%s : Press ENTER to continue" % (i, total))

def get_config_dirpath() -> str:
    return f'{os.getcwd()}/config'

def get_result_dirpath(folder) -> str:
    return f'{os.getcwd()}/results/{folder}'

def package_info(info: dict) -> pd.DataFrame:
    return pd.DataFrame(info.items(), columns=['Params', 'Value'])

def create_folder(path: str="XXX"):
    try:
        if not os.path.isdir(path):
            os.mkdir(path)
    except:
        raise NotADirectoryError(f"Error code {FOLDER_NOT_EXIST_ERR}: {error_message[FOLDER_NOT_EXIST_ERR]}")

def delete_folder(path: str="XXX"):
    try:
        if os.path.isdir(path):
            os.rmdir(path)
    except:
        raise NotADirectoryError(f"Error code {FOLDER_NOT_EXIST_ERR}: {error_message[FOLDER_NOT_EXIST_ERR]}")
    

def get_callable_funcs(cls, identifier):
    cls = type(cls) # get the class of the instance
    funcname_list = [method for method in dir(cls) if method.startswith(identifier)]
    func_list = [f'{i:20}:{cls.__dict__[i].__doc__}'.lstrip().rstrip() for i in funcname_list]
    func_str = "\n".join([i for i in func_list])
    return func_str


    
