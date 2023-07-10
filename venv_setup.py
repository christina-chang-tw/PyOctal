import os
import sys
import subprocess
import platform

requirements = "requirements.txt"
venv_path = f"{os.getcwd()}/.venv"
py = f"{os.getcwd()}/.venv/bin/python3"

if not os.path.dirname(sys.executable):
    raise Exception("Python Environment Not Found")

# Create a venv
subprocess.check_call([sys.executable, '-m', 'venv', venv_path])

print("Created a local Virtual Environment...")

subprocess.check_call([py, '-m', 'pip', 'install', '-r', requirements])

