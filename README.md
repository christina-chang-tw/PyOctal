# Optical Chip Optical Automated Testing 

## Setup Environment

**NOTE:** This automated optical chip testing only works with Windows OS machine.

Required packages: pandas, numpy, pywin32, pyvisa, argparse

Method 1:
Install Anaconda from its official site and make sure the listed packages are installed.

Method 2:

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
#

## Directory Structure

```
.
├── lib                      # test files (alternatively `spec` or `tests`)
│   ├── instruments          # containing instruments' calling functions 
│   ├── csv_operations.py    # csv file operations
│   ├── info.py              # test information
│   ├── sweeps.py            # automated testing sweeps
│   └── util.py              # general functions
├── results                  # store testing data
└── main.py                  # interface with the 
```

#

## Implemented Instruments

There are three instruments that are can be controlled remotely with this library.

| Filename | Instrument | Manufacturer |
| -------- | ---------- | ------------ |
| `dc_supply`  | E3640A Power Supply  | Keysight |
| `multimeter` | 8163B Lightwave Multimeter  | Keysight |
| `pas`        | Insertion Loss Measurement Engine | Keysight |


# 

## Tests and Setup Instrument
### Tests
These are the optical tests that are currently implemented by this library. These can be run by running `main.py` as a module from the root directory.

| Test    | Description    |
|---------|----------------|
| iloss   | Optain insertion loss and loss coefficient of the waveguide |

### Instrument setup
| Test    | Description    |
|---------|----------------|
| m_8163b | Setup the multimeter to the auto-range and desired wavelength and output power |

# 

## How to run a test?
Everything is this repository should be run as a python module.

```bash
# Example: 
# (1) General helper message
> python -m main -h
# (2) Helper message of the parameters for insertion loss test
> python -m main iloss -h
# (3) Running an insertion loss test with pout=10dBm and range=(1550, 1570)nm
> python -m main iloss -p 10 -r 1550 1570
```


#

## Debugging issues

1. f-string formatting method cannot be used is an issues related to the python version. Only versions after Python 3.6 adopts f-string format.




