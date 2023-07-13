import inspect
import sys

def get_func_name():
    return inspect.stack()[1].function

def wait_for_next_meas(i, total):
    print("\r")
    input("%s/%s : Press ENTER to continue" % (i, total))


def version_check():
    MIN_PYTHON = (3, 6)
    CUR_PYTHON = (sys.version_info.major, sys.version_info.minor)
    
    if sys.version_info < MIN_PYTHON:
        sys.exit("Python %s.%s or later is required. Current version: Python %s.%s\n" % (MIN_PYTHON + CUR_PYTHON))
