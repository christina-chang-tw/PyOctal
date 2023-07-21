# ORC Optical Chip Automated Testing Central Library

ORC OCATCL is a Python package equipped with all essential sweep tests, analysis tools, and interfaces with existing equipments in ORC group.

<!-- toc -->

- [More About ORC OCATCL](#more-about-orc-ocatcl)
  - [Directory Structure](#directory-structure)
- [Installation](#installation)
  - [Git Bash](#git-bash)
  - [Python Environment](#python-environment)
  - [Visual Studio Code (VSCode)](#visual-studio-code-vscode)
  - [Install ORC OCATCL](#install-orc-ocatcl)
- [Getting Started](#getting-started)
  - [How to Run a Test](#how-to-run-a-test)
  - [Test and Setup Instruments](#tests-and-setup-instrument)
  - [Debugging Issues](#debugging-issues)
- [Developer Guide](#developer-information)
  - [Git Bash](#git-bash-1)
  - [Expand this Library](#expand-this-library)


<!-- tocstop -->

## More About ORC OCATCL

### Directory Structure

```
.
├── config                   # all configuration files
├── lib                      # core library
├── results                  # store testing results
├── tests                    # contain simple instrument function tests <not implemented>
├── instr.py                 # direct interface with instruments (only for simple setup cases)
├── logging.log              # logging the output to a file
├── main.py                  # interface with running sweeps
├── plot.py                  # interface with plotting graphs
├── requirements.txt         # contain all required python packages for this repository <need to be amended>
└── venv_setup.py            # set up virtual environment <not working>
```

## Installation

### Git Bash

Install the newest correct version of Git for your Windows system. Git is a source distributed version control system designed to handle everything from small to very large projects with speed and efficiency. 

### Python Environment

This repository only works when two conditions are satisfied:
- Windows OS machine
- python version >= 3.6. 

**Method 1 (Preferred)**:

Install the newest correct version of Anaconda from its official site and make sure all listed packages in `requirements.txt` are installed. To install packages, go to Enviornments tab, select not installed, and then search up the packages. 


**Method 2 (Not working)**:

Run this in the root-directory of this repository namely `autotesting`.

| Platform | Shell   | Command to activate virtual environment
|----------|---------|----------------------------------------|
| Posix | bash/zsh   | $ source .venv/bin/activate |
|       | fish       | $ source .venv/bin/activate.fish |
|       | csh/tcsh   | $ source .venv/bin/activate.csh |
|       | PowerShell | $ .venv/bin/Activate.ps1 |
| Windows | cmd.exe    | > .venv\Scripts\activate.bat |
|         | PowerShell | > .venv\Scripts\Activate.ps1|

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


### Install ORC OCATCL

Getting the repository cloned to a local direcotory
```bash
# CLone this repository down to your current running directory
> git clone https://github.com/christina-chang-tw/autotesting.git
```

For users, I recommend to update your current old repository to a newer version by cloning this repository again and delete the old ones.

## Getting Started


### How to Run a Test?
Everything is this repository should be run as a python module. It uses argparse python package to parse command line information into the program. 

Before you run a test, please make sure that you set all parameters correctly in the corresponding configuration file! All configuration files are stored under `config` folder.

```bash
# Example: 
# (1) General helper message
> python -m main -h
# (2) Run a passive test
> python -m main -t passive
# (3) Run a passive test with a logging level of debug
> python -m main -t passive --log-lvl="DEBUG"
```
### Tests and Setup Instrument

These are the optical tests that are currently implemented by this library. These can be run by running `main.py` as a module from the root directory.

| Test (-t) | Description    |
|-----------|----------------|
| passive   | insertion loss testing |
| dc        | dc sweeps |


Run `instr.py` as a module.
| Test    | Description    |
|---------|----------------|
| m_8163b | Setup the multimeter to the auto-range and desired wavelength and output power |

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
> git pull https://github.com/christina-chang-tw/autotesting.git
```

Push your local changes to your remote branch:
```bash
> git add .
> git commit -m "message" # commit your local changes with "message" as a comment
> git push                # push your changes to remote branch
```

### Expand this library
To maintain the current structure, place your instrument class in the correct file. If the type of your instrument does not exist yet, please create a file with a general category of your instrument.



