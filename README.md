# Optical Chip Optical Automated Testing 

Repository last updated date: July 2023

## Directory Structure

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

## Setup Environment

**NOTE:** This automated optical chip testing only works for Windows OS machine with python version >= 3.6.

**Method 1 (Preferred)**:

Install Anaconda from its official site and make sure the listed packages in `requirements.txt` are installed. After installation of correct python version and packages, install Visual Studio Code (VSCode) and launch VSCode through Anaconda Navigator. 

Open a new bash terminal by going to the top tab bar and Terminal > New Terminal. Now you will have opened a terminal and ready to start running the program. Go to [User Information](#user-information) section for information about how to use this repository for your personal usage.


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

## User Information

### How to run a test?
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

## Tests and Setup Instrument
### Tests
These are the optical tests that are currently implemented by this library. These can be run by running `main.py` as a module from the root directory.

| Test      | Description    |
|-----------|----------------|
| passive   | insertion loss testing |
| dc        | dc sweeps |

### Instrument setup
| Test    | Description    |
|---------|----------------|
| m_8163b | Setup the multimeter to the auto-range and desired wavelength and output power |



## Debugging issues

1. f-string formatting method cannot be used is an issues related to the python version. Only versions after Python 3.6 adopts f-string format.


## Developer Information

### Expand this library
To maintain the current structure, place your instrument class in the correct file. If the type of your instrument does not exist yet, please create a file with a general category of your instrument.



