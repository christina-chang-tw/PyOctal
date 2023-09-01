""" 
This file contains all sorts of functions
that are used but do not belong to a specific category
"""
import inspect
import sys
import os
import logging
import pandas as pd

from pyoctal.error import *
from pyoctal.util.formatter import CustomLogFileFormatter, CustomLogConsoleFormatter
from . import __python_min_version__, __platform__


class DictObj:
    """ Convert a dictionary to python object """
    def __init__(self, **dictionary):
        self._dict = dictionary
        for key, val in dictionary.items():
            if isinstance(val, dict):
                self.__dict__[key] = DictObj(**val)
            else:
                self.__dict__[key] = val

    def __getitem__(self, key):
        return self.__dict__[key]

    def keys(self):
        return self.__dict__.keys()

    def get(self, key):
        if key in self.__dict__.keys():
            return self.__getitem__(key)
        return None
    
    @property
    def dict(self):
        return self._dict

def setup_rootlogger(root_logger, fname: str):
    root_logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(filename=fname, mode='w') # output loggings to logging.log
    file_handler.setFormatter(CustomLogFileFormatter())
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomLogConsoleFormatter())
    root_logger.addHandler(console_handler)


def platform_check():
    """ Check if the OS is Windows. """
    if sys.platform not in __platform__:
        raise SystemError("Error code %s: %s. Current platform is %s" % (INCOMPATIBLE_OS_ERR, error_message[INCOMPATIBLE_OS_ERR], sys.platform))
    

def pyversion_check():
    """ Check that the python version >= Python 3.6. """
    MIN_PYTHON = __python_min_version__
    CUR_PYTHON = (sys.version_info.major, sys.version_info.minor)
    if sys.version_info <= MIN_PYTHON:
        raise SystemError("Error code %s: %s. Python %s.%s or later is required. Current version: Python %s.%s\n" % (PYTHON_VER_ERROR, error_message[PYTHON_VER_ERROR], MIN_PYTHON[0], MIN_PYTHON[1], CUR_PYTHON[0], CUR_PYTHON[1]))


def get_func_name() -> str:
    return inspect.stack()[1].function

def wait_for_next_meas(i, total):
    print("\r")
    input(f"{i}/{total} : Press ENTER to continue")


def get_config_dirpath() -> str:
    return f'{os.getcwd()}/config'


def get_result_dirpath(folder) -> str:
    return f'{os.getcwd()}/results/{folder}'

def package_info(info: dict) -> pd.DataFrame:
    """ Put information about a sweep into a dataframe. """
    return pd.DataFrame(info.items(), columns=['Params', 'Value'])

def create_folder(path: str="XXX"):
    if not os.path.isdir(path):
        os.mkdir(path)

def delete_folder(path: str="XXX"):
    if os.path.isdir(path):
        os.rmdir(path)

def get_callable_funcs(obj, identifier: str="") -> str:
    """ Get all callable (unhidden) functions of a class in a nice format style. """ 

    func, _ = zip(*inspect.getmembers(object=obj, predicate=inspect.isfunction))
    
    correct_func = []
    for obj in func:
        if not obj.startswith('__') and not obj.startswith('_'):
            correct_func.append(obj)

    return correct_func


    
