from argparse import ArgumentParser
import yaml
from pyvisa import ResourceManager

from pyoctal.instruments import Agilent8163B, AgilentE3640A, Agilent8164B

def main():
    parser = ArgumentParser()
    parser.add_argument("name", help="Name of the setup")
    parser.add_argument("--file", help="Path to the setup file", default="tools/setups/config.yaml")
    
    args = parser.parse_args()

    print(f"Setting up {args.name} from {args.file}")

    # Read the setup file
    with open(args.file, "r", encoding="utf-8") as file:
        setups = yaml.load(file)

    # Check if the setup exists
    if args.name not in setups.keys():
        raise ValueError(f"Setup {args.name} not found in {args.file}")
    
    setup = setups[args.name]

    # Import the setup class
    rm = ResourceManager()
    cls = globals()[setup["class"]]
    cls = cls(addr=setup["addr"], rm=rm)

    # Setup the instrument
    print("Setting up the instrument.")
    if setup["class"] in (Agilent8163B, Agilent8164B):
        if setup["op_operation"]:
            wavelength = cls.find_op_wavelength(**setup["op_config"])
            setup["wavelength"] = wavelength
        cls.setup(**setup)

    elif setup["class"] == AgilentE3640A:
        cls.setup(**setup)
    print("Setup complete.")

if __name__ == "__main__":
    main()