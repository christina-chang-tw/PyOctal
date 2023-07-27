""" Setup a python virtual environment """

import os
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)

requirements = "requirements.txt"
venv_path = os.getcwd() + r"/.venv"
py = os.getcwd() + r"/.venv/bin/python3"

if not os.path.dirname(sys.executable):
    logger.error("Python Environment Not Found")

try:
    if sys.version_info[0] < 3:
        raise SystemError("Please update your Python version to 3.0 later")
    subprocess.check_call([sys.executable, '-m', 'venv', venv_path])
    print("Created a local Virtual Environment...")
    subprocess.check_call([py, '-m', 'pip', 'install', '-r', requirements])
    print("Everything are successfully installed")

except Exception as error:
    print("Certain modules cannot be imported")
    raise error
