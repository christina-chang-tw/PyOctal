""" Setup a python virtual environment """

import os
import sys
import subprocess
import platform
import warnings


requirements = os.getcwd() + r"/requirements.txt"
venv_path = os.getcwd() + r"/.venv"
venv_py = os.getcwd() + r"/.venv/bin/python3"

try:
    if not os.path.dirname(sys.executable):
        raise SystemError("Python Environment Not Found")
    if sys.version_info[0] < 3:
        raise SystemError("Please update your Python version to 3.0 later")
    subprocess.check_call([sys.executable, '-m', 'venv', venv_path])
    print("A local virtual environment is created...")
    subprocess.check_call([venv_py, '-m', 'pip', 'install', '-r', requirements])
    print()
    if not platform.system == "Windows":
        print("WARNING: NOT WINDOWS SYSTEM")
        print("Cannot install win32 so please don't use classes requiring it. Otherwise, you are good to go.")
    else:
        print("Everything is successfully installed. Congrats!")
    print()

except SystemError as error:
    raise error
