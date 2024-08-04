"""
main.py
=======
This script is used to setup the instruments based on the configuration file.
The configuration file is a YAML file that contains the setup for the instruments 
default to tools/setups/config.yaml.

To run this script:
    python -m tools.setups.main <name> [--file <path_to_file>]
"""
from typing import Union

from argparse import ArgumentParser
import yaml
from pyvisa import ResourceManager

from pyoctal.instruments import Agilent8163B, AgilentE3640A, Agilent8164B

def main():
    """ Entry point."""
    parser = ArgumentParser()
    parser.add_argument("name", help="Name of the setup")
    parser.add_argument("--file", help="Path to the setup file",
                        default="tools/setups/config.yml", required=False)

    args = parser.parse_args()

    print(f"Setting up {args.name} from {args.file}")

    # Read the setup file
    with open(args.file, "r", encoding="utf-8") as file:
        setups = yaml.load(file, Loader=yaml.FullLoader)

    # Check if the setup exists
    if args.name not in setups.keys():
        raise ValueError(f"Setup {args.name} not found in {args.file}. \
                         Make sure that the name matches!")

    setup = setups[args.name]

    # Import the setup class
    rm = ResourceManager()
    cls = globals()[setup.pop("class")]
    cls = cls(addr=setup.pop("addr"), rm=rm)

    # Setup the instrument
    if isinstance(cls, Union[Agilent8163B, Agilent8164B]):
        if setup["op_operation"]:
            wavelength = cls.find_op_wavelength(**setup["op_config"])
            setup["wavelength"] = wavelength
        cls.setup(**setup)

    elif isinstance(cls, AgilentE3640A):
        cls.setup(**setup)
    print("Setup complete.")

if __name__ == "__main__":
    main()
