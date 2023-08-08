from lib.error import *

import pyvisa
import logging
from typing import Union
import textwrap

logger = logging.getLogger(__name__)

def list_resources():
    """
    Function that prints and returns a list with all the available resources in the PC. 
    """
    # List of the available resources
    resources = pyvisa.ResourceManager().list_resources()
    print('Available resources in the PC:')
    print(resources)
    return resources


class DeviceID:
    """
    Device identity

    Parameters
    ----------
    idn: str
        string returned from querying IDN*?
    """
    def __init__(self, idn: str):
        strip_idn = idn.split(',')
        self._vendor = strip_idn[0]
        self._modelno = strip_idn[1]
        self._serialno = strip_idn[2]
        self._version = strip_idn[3]

    def __repr__(self):
        return "Device ID()"
    
    def __str__(self):
        text = textwrap.dedent(f"""
            {'Vendor':<10} : {self._vendor}
            {'Model No.':<10} : {self._modelno}
            {'Serial No.':<10} : {self._serialno}
            {'Version':<10} : {self._version}
        """)
        return text.lstrip().rstrip()
    
    @property
    def vendor(self):
        return self._vendor
    @property
    def modelno(self):
        return self._vendor
    @property
    def serialno(self):
        return self._serialno
    @property
    def version(self):
        return self._version


class BaseInstrument(object):
    """
    A base instrument class containing minimum useful and compatible functions.

    Parameters
    ----------
    rsc_addr: str
        The address that the instrument displayed on the computer.
        It can be either a GPIB, RS232, USB, or an Ethernet address.
    termination: str
        The termination character when pyvisa is communicating with the instrument
    """
    def __init__(self, rsc_addr, termination: str='\n'):
        # Communicate with the resource and identify it
        self._addr = rsc_addr
        self._rm = pyvisa.ResourceManager()
        self._rm.timeout = 20000
        self._rm.read_termination = termination
        
        # Connect to the device
        if rsc_addr in self.list_resource(): # Checking if the resource is available
            self.instr = self._rm.open_resource(rsc_addr)
            instr_type = self.instr.resource_info[3][:4]
            known_type = ("ASRL", "GPIB", "USB", "PXI", "VXI", "TCPIP")

            # make sure that we know the device type
            if instr_type not in known_type:
                raise Exception(f"Error code {RESOURCE_CLASS_UNKNOWN_ERR:x}: {error_message[RESOURCE_CLASS_UNKNOWN_ERR]}")
            print(f'You have connected succesfully with a/an {instr_type} type resource')

            self._identity = DeviceID(self.get_idn())
        else:
            raise Exception(f"Error code {RESOURCE_ADDR_UNKNOWN_ERR:x}: {error_message[RESOURCE_ADDR_UNKNOWN_ERR]}")

    def list_resource(self):
        return self._rm.list_resources()
            
    @staticmethod
    def value_check(value, cond: Union[tuple, list]=None):
        if cond is None: # nothing to check for
            pass
        elif not isinstance(cond, Union[tuple, list]) or all(cond): # the condition is incorrectly set and they are of the same type
            raise ValueError(f"Error code {COND_INVALID_ERR:x}: {error_message[COND_INVALID_ERR]}")
        elif len(cond) == 2 and all(isinstance(n, Union[float, int]) for n in cond):
            if not cond[0] < value < cond[1]: # check the value is within range
                raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}.\nNeed to be between {cond[0]} and {cond[1]}.")
        else:
            if value not in cond: # check the value is in a list/tuple
                raise ValueError(f"Error code {PARAM_INVALID_ERR:x}: {error_message[PARAM_INVALID_ERR]}.\nPlease select one of the values: {[', '.join(val) for val in cond]}")


    def write(self, cmd):
        self.instr.write(cmd)
    
    def write_binary_values(self, cmd):
        self.instr.write_binary_values(cmd)
    
    def read(self, cmd) -> str:
        return self.instr.read(cmd).rstrip()
    
    def query(self, cmd) -> str:
        return self.instr.query(cmd).rstrip()
    
    def query_bool(self, cmd) -> bool:
        return bool(self.instr.query(cmd).rstrip())
    
    def query_float(self, cmd) -> float:
        return float(self.instr.query(cmd).rstrip())
    
    def query_binary_values(self, cmd) -> list:
        return self.instr.query_binary_values(cmd, is_big_endian=False)
    
    def get_idn(self) -> str:
        return self.query("*IDN?")

    def reset(self):
        self.write("*RST")

    def clear(self):
        self.write("*CLS")

    def opc(self) -> bool:
        return self.query("*OPC?")
    
    def err(self) -> str:
        return self.query("system:error?")

    @property
    def identity(self) -> str:
        return self._identity
    
    @property
    def address(self) -> str:
        return self._addr
    
    @property
    def rm(self):
        return self._rm

    def __get_name(self) -> str:
        return self.__class__.__name__
    
    def __str__(self) -> str:
        return f"Instrument: {self.__get_name()} "
    
    def __repr__(self) -> str:
        return f"{self.__get_name()}({self.instr, self.identity})"


class BaseSweeps(object):
    """
    A base sweep class

    Parameters
    ----------
    instr: an instrument class
        This is the instrument that is used in the sweep
    """
    def __init__(self, instr_addrs, folder, fname):
        self._addrs = instr_addrs
        self.folder = folder
        self.fname = fname

    def __str__(self) -> str:
        return f"Sweep: {self.__class__.__name__} "
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
    
    @property
    def addrs(self):
        return self._addrs
    
    @staticmethod
    def instrment_check(match, addr_list):
        if isinstance(match, str) and match not in addr_list:
            raise Exception(f"Error code {INSTR_NOT_EXIST:x}: {error_message[INSTR_NOT_EXIST]}")
        elif isinstance(match, Union[tuple, list]) and not all([dev_type in addr_list for dev_type in match]):
            raise Exception(f"Error code {INSTR_NOT_EXIST:x}: {error_message[INSTR_NOT_EXIST]}")
        else:
            raise Exception(f"Error code {INSTR_MATCH_STRING_INCOR}: {error_message[INSTR_MATCH_STRING_INCOR]}")

    @classmethod
    def get_callable_funcs(cls):
        method_list = [method for method in dir(cls) if method.startswith('__') is False or method.startswith('_') is False]

        # filter out specific ones
        method_list = filter(lambda x: x.startswith("run_"), method_list)
        return method_list
    
