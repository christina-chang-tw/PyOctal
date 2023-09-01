# Library

The core library of this project.

### Directory Structure
```
lib
├── instruments              # library for instruments' commands
│   └── ...                         # read the README.md
├── sweeps                   # different types of sweeps
│   ├── ac.py                       # ac sweeps
│   ├── dc.py                       # dc sweeps
│   └── passive.py                  # passive test sweeps
├── util                     # utility library
│   ├── file_operations.py          # functions related to read/writing to a file
|   ├── formatter.py                # contain all customised formatter classes
│   ├── plot.py                     # plotting graphs and analyze data
│   └── util.py                     # general utility library
├── base.py                  # contain all base classes
└── error.py                 # customised error messages
```