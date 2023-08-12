import os
from glob import glob
import importlib
import inspect
import pyvisa
import yaml

from pyoctal.base import DeviceID
from pyoctal.util.util import get_callable_funcs

class TestClassCalls:
    sim_fpath = './tests/sim_dev.yaml'
    sim_rm = sim_fpath + '@sim'
    
    def test_instr_initialization(self):
        """ Test that the instruments can all be connected. """

        with open(file=self.sim_fpath, mode='r') as file:
            configs = yaml.safe_load(file)

        # get parameters straight from the yaml file
        
        rm = pyvisa.ResourceManager(self.sim_rm)
        addr = rm.list_resources()[0]
        identity = configs["devices"]["device 1"]["dialogues"][0]["r"]
        rm.close()
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
                if member in ['BaseInstrument','KeysightFlexDCA'] + tested_module or member.__str__().startswith('__'):
                    continue
                tested_module.append(member)
                # initialise a device
                dev = cls(addr=addr, rm=self.sim_rm)
                # check that the ids are as expected
                assert DeviceID(identity) == dev.identity

    
    def test_class_docstrings(self):
        """ Test that the instruments all have a class docstring and display it when tested. """

        # get the address from opening up another resource manager
        rm = pyvisa.ResourceManager(self.sim_rm)
        addr = rm.list_resources()[0]
        rm.close()
        tested_module = []

        # search through the name of the files matching *.py under the folder
        print()
        print("-"*117)
        print(f'| {"Class":<20} | {"Description":<90} |')
        print("-"*117)
        for file in glob(os.path.join("./pyoctal/instruments" + "/*.py")):
            name = os.path.splitext(os.path.basename(file))[0]
            # ignore the two classes as they are not inherited from BaseInstrument class
            if name in ("thorlabsAPT", 'keysightPAS'):
                continue
            module = f'pyoctal.instruments.{name}'
            # perform dynamic import
            for member, cls in inspect.getmembers(importlib.import_module(module), inspect.isclass):
                if member in ['BaseInstrument','KeysightFlexDCA'] + tested_module or member.__str__().startswith('__'):
                    continue
                # make sure that tested modules won't be tested again
                tested_module.append(member)
                
                dev = cls(addr=addr, rm=self.sim_rm) # initialise a device
                doc = cls.__doc__.split('.')[0].rstrip().lstrip()
                dev.close()
                print(f"| {member:20} | {doc:90} |")
        print("-"*117)


def test_callable_funcs():
    from pyoctal.base import BaseInstrument
    funcs = get_callable_funcs(obj=BaseInstrument)
    test_funcs = ['write', 'query', 'get_idn'] # only testing a fraction of callable functions
    assert [name for name in test_funcs if name in funcs]