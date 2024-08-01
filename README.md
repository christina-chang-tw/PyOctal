# PyOctal

PyOctal is a Python package equipped with sweep tests, analysis tools, and interfaces with equipments that are used primarily for optical chip testing.
This package supports visa communications with a varitey of instruments.

<!-- toc -->
- [More About PyOctal](#more-about-pyoctal)
- [Directory Structure](#directory-structure)
- [Installation](#installation)
  - [Git Bash](#git-bash)
  - [Python Environment](#python-environment)
  - [Visual Studio Code (VSCode)](#visual-studio-code-vscode)
  - [Install PyOctal](#install-pyoctal)
- [Getting Started](#getting-started)
  - [How to Run a Test](#how-to-run-a-test)
  - [Test and Setup Instruments](#tests-and-setup-instrument)
  - [Debugging Issues](#debugging-issues)
- [Developer Guide](#developer-information)
  - [Git Bash](#git-bash-1)
  - [Expand this Library](#expand-this-library)
<!-- tocstop -->


## More About PyOctal
This is a tool allowing you to do three things: remotely setup your instruments, run different types of sweeps, and analyse the results afterwards. This is still at its infancy stage so is still lacking a lot of functions which are widely used by the users. Please suggest and we would love to help!

Take a look at [here](https://github.com/christina-chang-tw/PyOctal/blob/master/pyoctal/instruments/README.md) for detailed information of supported instruments.

## Directory Structure
```
.
<folders>
├── config                   # all configuration files
│   └── ...                         # read the README.md
├── pyoctal                  # core library
│   └── ...                         # read the README.md
├── results                  # all test results should be stored here <empty>
├── tools                    # all test results should be stored here
│   |── plot_main.py                # plotting graphs
│   |── instr_main.py               # simple interface for setting up instruments
│   └── sweep_main.py               # interface for running sweeps
<files>
├── pyproject.toml           # pyoctal package setup 
├── requirements.txt         # contain all required python packages for this repository <need to be amended>
└── venv_setup.py            # set up virtual environment <not working>
```

## Installation

Before installing any of the software, please make sure that you know exactly the operating system that you are running on and whether it is 32-bit or 64-bit.

### Environment

This repository only works when two conditions are satisfied:
- Windows OS machine - this is neccessary for pywin32 module
- python version >= 3.6 - this is neccessary for f-string formatting

**Method 1 - Install Anaconda (Preferred)**:

The Anaconda version must
- Support your current Windows OS system
- Able to create a Python 3.6 environment

Install Anaconda version which supports your OS system and make sure all Listed packages in `requirements.txt` are installed.

To install packages, go to Enviornments tab, select not installed, and then search up the packages. There are some packages that might not be Listed because the channel which contain them are not imported upon installation. If that is the case, search up the python package and find the corresponding channel and include it in Anaconda environment. 

If your Anaconda does not use Python 3.6 for its environment, it will fail to install `pyvisa`. Firstly, make sure that the current Anaconda python version is at least 3.6. Once the condition is satisfied, create a new environment with Anaconda Prompt and specify Python version as Python 3.6. After the new environment is successfully created, it can be viewed under Environments tab. The packages can then be installed on this new environment without errors.

```bash
# create a new conda environment
> conda create --name pyoctal_env python=<version>
# activate your new environment
> conda activate pyoctal_env
# deactivate
> conda deactivate
```

- `pyvisa` requires "conda-forge" channel
- `pyaml` requires "conda-forge" channel

**NOTE FOR WINDOWS 7 USERS:**
If your system is running on Windows 7, please only install Anaconda versions which are equipped with Python versions older than 3.8. This is very important as versions since Python 3.9 do not support Windows 7. The safe option is install versions before anaconda3-2020-11. 

If you attempt to install the later anaconda version on your Windows 7 system, you will get a "Failed to create menus" error. Refer to [Using Anaconda on older operating systems](https://docs.anaconda.com/free/anaconda/install/old-os/) for more information.


**Method 2 - Use Virtual Python Environment**:

Run this in the root-directory of this repository namely `autotesting`.

| Platform | Shell   | Command to activate virtual environment
|----------|---------|----------------------------------------|
| Posix    | bash/zsh   | $ source .venv/bin/activate |
|          | fish       | $ source .venv/bin/activate.fish |
|          | csh/tcsh   | $ source .venv/bin/activate.csh |
|          | PowerShell | $ .venv/bin/Activate.ps1 |
| Windows  | cmd.exe    | > .venv\Scripts\activate.bat |
|          | PowerShell | > .venv\Scripts\Activate.ps1|

```bash
# This automatically setup your virtual environment
> python3 -m venv_setup

# Windows PS example
# Activate a venv machine.
> .venv\Scripts\Activate.ps1

# Deactivate a venv machine
> deactivate
```
### Install PyOctal

For users, I recommend to update your current old repository to a newer version by cloning or downloading this repository again and delete the old ones.

**Method 1 - Clone from Git (Preferred)**:

Getting the repository cloned to a local direcotory
```bash
# Create a directory named autotesting
> mkdir pyoctal
# Go into that directory
> cd pyoctal
# Clone this repository down to your autotesting directory
> git clone https://github.com/christina-chang-tw/PyOctal.git
# move into that directory
> cd PyOctal
```

**Method 2 - Download from Github**:

You can download a zip file containing this repository by navigating to <> Code tab and then select Local and Download ZIP.

**Method 3 - Pip Installation**

This package supports installation using pip allowing users to expand the project further. The usage is just like other python packages.

```bash
> python -m pip install pyoctal
```


## Getting Started

### How to Run a Test?
Everything is this repository should be run as a python module. It uses argparse package to parse command line information to the program. You should pass in a .yaml file to set all the parameters.

**Sweeps**

These are the optical tests that are currently implemented by this library. These can be run by running `sweep_main.py` as a module from the root directory.

| Tests     | Instruments  | Description    |
| --------- | ------------ | -------------- |
| passive   | ILME, Agilent 8163B | Insertion loss testing using PAS ILME engine |
|           | Agilent 8163B       | Manual insertion loss testing |
| dc        | | dc sweeps |

Before you run a test, please make sure that you set all parameters correctly in the corresponding configuration file! All configuration files should be stored under `config` folder.

```bash
# Example: 
# (1) General helper message
> python -m tools.sweep_main -h
# (2) Run a passive test without specifying anything
> python -m tools.sweep_main -t passive
# (3) Run a dc sweep test with logging level as DEBUG and specify the config file path
> python -m tools.sweep_main -t dc --config ./config/test.yaml
```

**Instrument Setup**

An interface to easily setup an instrument.
| Test    | Instrument | Description    |
|---------| ---------- |----------------|
| agilent8163B | Agilent 8163B | Setup the multimeter to the auto-range and desired wavelength and output power |
| h_speed | Setup the clock frequency for both clock signal generator and oscilloscope |

```bash
# Example: 
# (1) General helper message
> python -m tools.instr_main -h
# (2) Helper message for specific instrument(s)
> python -m tools.instr_main agilent8163B -h
# (3) Setup 8163B wavelength at 1550nm and power at 10dBm
> python -m tools.instr_main agilent8163B -w 1550 -p 10
```

### Debugging issues

1. f-string formatting method cannot be used is an issues related to the python version. Only versions after Python 3.6 adopts f-string format.
2. Contact me if need extra help: tyc1g20@soton.ac.uk 
