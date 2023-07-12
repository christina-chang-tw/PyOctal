import inspect
import sys

def get_func_name():
    return inspect.stack()[1].function

def wait_for_next_meas():
    input("Press ENTER to continue to the next test...")
    sys.stdout.write("\033[F") #back to previous line 
    sys.stdout.write("\033[K") #clear line

def version_check():
    MIN_PYTHON = (3, 6)
    CUR_PYTHON = (sys.version_info.major, sys.version_info.minor)
    
    if sys.version_info < MIN_PYTHON:
        sys.exit("Python %s.%s or later is required. Current version: Python %s.%s\n" % (MIN_PYTHON + CUR_PYTHON))
