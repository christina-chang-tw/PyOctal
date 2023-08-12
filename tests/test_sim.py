import pyvisa

from pyoctal.instruments import Agilent8163B
from pyoctal.base import DeviceID

sim_fpath = './tests/sim_dev.yaml@sim'

def test_simdev():
    rm = pyvisa.ResourceManager(sim_fpath)
    assert rm is not None

def test_instr_initialization():
    import os
    from glob import glob
    import yaml
    import importlib
    import inspect

    with open(file="./tests/sim_dev.yaml", mode='r') as file:
        configs = yaml.safe_load(file)

    # get parameters straight from the yaml file
    addr = list(configs['resources'].keys())[0]
    identity = configs['devices']['device 1']['dialogues'][0]['r']
    tested_module = []

    # search through the name of the files matching *.py under the folder
    for file in glob(os.path.join("./pyoctal/instruments" + "/*.py")):
        name = os.path.splitext(os.path.basename(file))[0]
        # ignore the two classes as they are not inherited from BaseInstrument class
        if name in ("thorlabsAPT", 'keysightPAS'):
            continue
        module = f'pyoctal.instruments.{name}'

        # perform dynamic import
        for member, cls in inspect.getmembers(importlib.import_module(module), inspect.isclass):
            tested_module.append(member)
            if member in ['BaseInstrument','KeysightFlexDCA'] + tested_module or member.__str__().startswith('__'):
                continue
            # initialise a device
            dev = cls(addr=addr, rm=sim_fpath)
            # check that the ids are as expected
            assert DeviceID(identity) == dev.identity