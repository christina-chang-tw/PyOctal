# ORC Optical Chip Test Automation Library

ORC OCTAL is a Python package equipped with all essential sweep tests, analysis tools, and interfaces with existing equipments in ORC group.

<!-- toc -->
- [More About ORC OCTAL](#more-about-orc-octal)
  - [Directory Structure](#directory-structure)
- [Installation](#installation)
  - [Git Bash](#git-bash)
  - [Python Environment](#python-environment)
  - [Visual Studio Code (VSCode)](#visual-studio-code-vscode)
  - [Install ORC OCTAL](#install-orc-octal)
- [Getting Started](#getting-started)
  - [How to Run a Test](#how-to-run-a-test)
  - [Test and Setup Instruments](#tests-and-setup-instrument)
  - [Debugging Issues](#debugging-issues)
- [Developer Guide](#developer-information)
  - [Git Bash](#git-bash-1)
  - [Expand this Library](#expand-this-library)
<!-- tocstop -->


## More About ORC OCTAL
This is a tool allowing you to do three things: remotely setup your instruments, run standard sweeps, and analyse the results afterwards which all files should have a specific format. This is still at its infant stage so is still lacking a lot of functions which are widely used by the users. Please suggest and we would love to help!

### Directory Structure

```
.
<folders>
├── config                   # all configuration files
├── lib                      # core library
├── results                  # store testing results
├── tests                    # contain unit testing for functions (users please ignore)
<files>
├── instr.py                 # direct interface with instruments (only for simple setup cases)
├── logging.log              # logging the output to a file
├── main.py                  # interface with running sweeps
├── plot.py                  # interface with plotting graphs
├── requirements.txt         # contain all required python packages for this repository <need to be amended>
└── venv_setup.py            # set up virtual environment <not working>
```

## Installation

Before installing any of the software, please make sure that you know exactly the operating system that you are running on and whether it is 32-bit or 64-bit.

### Git Bash (Optional)

If you have not install Git, install the newest correct version of Git for your Windows system. Git is a source distributed version control system designed to handle everything from small to very large projects with speed and efficiency. This is a very useful tool to keep track of the newest information being pushed onto the remote Github repository.

### Environment

This repository only works when two conditions are satisfied:
- Windows OS machine - this is neccessary for pywin32 module
- python version >= 3.6 - this is neccessary for f-string formatting

**Method 1 - Install Anaconda (Preferred)**:

The Anaconda version must
- Support your current Windows OS system
- Able to create a Python 3.6 environment

Install Anaconda version which supports your OS system and make sure all listed packages in `requirements.txt` are installed.

To install packages, go to Enviornments tab, select not installed, and then search up the packages. There are some packages that might not be listed because the channel which contain them are not imported upon installation. If that is the case, search up the python package and find the corresponding channel and include it in Anaconda environment. 

If your Anaconda does not use Python 3.6 for its environment, it will fail to install `pyvisa`. Firstly, make sure that the current Anaconda python version is at least 3.6. Once the condition is satisfied, create a new environment with Anaconda Prompt and specify Python version as Python 3.6. After the new environment is successfully created, it can be viewed under Environments tab. The packages can then be installed on this new environment without errors.

```bash
# create a new conda environment
> conda create --name orc_octal python=3.6
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

### Visual Studio Code (VSCode)

Install VSCode for code editing or running in python terminal. This software can be opened in Anaconda Navigator under Home tab. Recommend you to setup a Github account if you have not already done so and sign in to the account in VSCode.

Open a new bash terminal in VSCode by going to the top tab bar and Terminal > New Terminal. Now you will have opened a terminal and ready to clone the repository down.

**NOTE:** If you are running Windows 7, alternative code editors, such as Atom, VSCodium, and Texteditor are available.


### Install ORC OCTAL

For users, I recommend to update your current old repository to a newer version by cloning or downloading this repository again and delete the old ones.

**Method 1 - Clone from Git (Preferred)**:

Getting the repository cloned to a local direcotory
```bash
# Create a directory named autotesting
> mkdir autotesting
# Go into that directory
> cd autotesting
# Clone this repository down to your autotesting directory
> git clone https://github.com/christina-chang-tw/ORCOCTAL.git
# move into that directory
> cd ORCOCTAL
```

**Method 2 - Download from Github**:

You can download a zip file containing this repository by navigating to <> Code tab and then select Local and Download ZIP.

## Getting Started

### Launch terminal

Launch the Anaconda prompt either via search result or Anaconda Navigator. Once it is launched, activate the new environment (orc_octal). Now, you are all set to run your tests.

```bash
# activate your new environment
> conda activate orc_octal
# deactivate
> conda deactivate
```

### How to Run a Test?
Everything is this repository should be run as a python module. It uses argparse package to parse command line information to the program. 

**Sweeps**

These are the optical tests that are currently implemented by this library. These can be run by running `main.py` as a module from the root directory.

| Tests     | Instruments  | Description    |
| --------- | ------------ | -------------- |
| passive   | ILME, Agilent 8163B | Insertion loss testing using PAS ILME engine |
|           | Agilent 8163B       | Manual insertion loss testing |
| dc        | | dc sweeps |

Before you run a test, please make sure that you set all parameters correctly in the corresponding configuration file! All configuration files should be stored under `config` folder.

```bash
# Example: 
# (1) General helper message
> python -m sweep_main -h
# (2) Run a passive test without specifying anything
> python -m sweep_main -t passive
# (3) Run a dc sweep test with logging level as DEBUG and specify the config file path
# -<var>=<str> or -<var> <str> yields the same result
> python -m sweep_main -t dc --log-lvl DEBUG --config=./config/test.yaml
```

**Instrument Setup**

Run `instr.py` as a module.
| Test    | Description    |
|---------|----------------|
| m_8163b | Setup the multimeter to the auto-range and desired wavelength and output power |
| h_speed | Setup the clock frequency for both clock signal generator and oscilloscope |

```bash
# Example: 
# (1) General helper message
> python -m instr_main -h
# (2) Helper message for specific instrument(s)
> python -m instr_main m_8163b -h
# (3) Setup 8163B wavelength at 1550nm and power at 10dBm
> python -m instr_main m_8163b -w 1550 -p 10
```

### Debugging issues

1. f-string formatting method cannot be used is an issues related to the python version. Only versions after Python 3.6 adopts f-string format.
2. Contact me if need extra help: tyc1g20@soton.ac.uk 


## Developer Information

### Git Bash

Git commands related to updating the remote directory. The best practice is 
- Create a new branch before making any modifictions to the repository as it isolates out your changes from others
- Always pull the newest update before you push your new changes
- Once you are satisfied and ready to make the final update to the main reponsitory, merge your branch and the main branch together

Create a branch for developing your own code:
```bash
# Example
> git branch new_branch # create a new branch called new_branch
> git checkout new_branch # checkout to new_branch from current branch
```


Pull the newest changes down:
```bash
> git pull 
# or
> git pull https://github.com/christina-chang-tw/orcoctal.git
```

Push your local changes to the remote repository:
```bash
> git add .
> git commit -m "message" # commit your local changes with "message" as a comment
> git push                # push your changes to the remote branch
```

### Expand this library
To maintain the current structure, place your instrument class in the correct file. If the type of your instrument does not exist yet, please create a file with a general category of your instrument.



