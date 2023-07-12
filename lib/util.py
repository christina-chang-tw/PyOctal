import inspect
import sys

def get_func_name():
    return inspect.stack()[1].function

def wait_for_next_meas():
    input("Press ENTER to continue to the next test...")
    sys.stdout.write("\033[F") #back to previous line 
    sys.stdout.write("\033[K") #clear line

