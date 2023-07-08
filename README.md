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
└── main.py                  # interface with the 
```
# 

## How to use this?
Everything is this repository should be run as a python module.

```bash
# Example: this calls the main.py as a python module
> python -m main
```




