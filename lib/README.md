# Library

The core library of this project.

### Directory Structure
```
lib
├── analysis                 # post-processing data library
│   ├── iloss                       # generate loss coefficient and insertion loss
│   └── plt.py                      # plot data
├── instruments              # each instrument's library
│   └── ...                         # read the README.md
├── sweeps                   # direct interface with instruments
│   ├── ac.py                       # ac sweeps
│   ├── dc.py                       # dc sweeps
│   ├── info.py                     # information of each sweep (to be exported to a .csv file)
│   └── passive.py                  # passive test sweeps
├── util                     # utility library
│   ├── file_operations.py          # functions related to read/writing to a file
│   ├── logger.py                   # functions related to loggers
│   └── util.py                     # general utility library
└── base.py                  # contain all base classes
```