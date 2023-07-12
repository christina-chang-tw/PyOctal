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

if sys.version_info[0] < 3:
    subprocess.check_call([sys.executable, '-m', 'pip', "install", "virtualenv"])
    subprocess.check_call([sys.executable, '-m', 'pip', "install", "virtualenv"])



subprocess.check_call([sys.executable, '-m', 'venv', venv_path])

print("Created a local Virtual Environment...")

subprocess.check_call([py, '-m', 'pip', 'install', '-r', requirements])

