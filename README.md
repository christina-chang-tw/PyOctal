# Optical Chip Optical Automated Testing 

## Setup Environment

**NOTE:** This automated optical chip testing only works with Windows OS machine.**


Install Anaconda from its official site and make sure the following listed packages are installed.

- pandas
- pywin32
- pyvisa
- argparse

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




