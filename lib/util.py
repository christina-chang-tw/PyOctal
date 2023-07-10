import inspect

def get_func_name():
    return inspect.stack()[1].function

def wait_for_next_meas():
    input("Press ENTER to continue...")
    print("Continue to the next test...")

