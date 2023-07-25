from lib.error import *

import win32com.client
import pyvisa
import time
import logging
from typing import Union

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
        try: 
            if rsc_addr in self.list_resource(): # Checking if the resource is available
                self.instr = self._rm.open_resource(rsc_addr)
                instr_type = self.instr.resource_info[3][:4]
                known_type = ("ASRL", "GPIB", "USB", "PXI", "VXI", "TCPIP")

                # make sure that we know the device type
                if instr_type not in known_type:
                    raise Exception(f"Error code {RESOURCE_CLASS_UNKNOWN_ERR:x}: {error_message[RESOURCE_CLASS_UNKNOWN_ERR]}")
                print(f'You have connected succesfully with a/an {instr_type} type resource')

                self._identity = self.get_idn()
            else:
                raise Exception(f"Error code {RESOURCE_ADDR_UNKNOWN_ERR:x}: {error_message[RESOURCE_ADDR_UNKNOWN_ERR]}")
        
        except Exception as e:
            print(e)

    def list_resource(self):
        return self._rm.list_resources()
            
    @staticmethod
    def value_check(value, cond: Union[tuple, list]=None):
        try:
            if cond is None: # nothing to check for
                pass
            elif not isinstance(cond, Union[tuple, list]) or all(cond): # the condition is incorrectly set and they are of the same type
                raise ValueError(f"Error code {COND_INVALID_ERR:x}: {error_message[COND_INVALID_ERR]}")
            elif len(cond) == 2 and all(isinstance(n, Union[float, int]) for n in cond):
                if not cond[0] < value < cond[1]: # check the value is within range
                    raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: {error_message[PARAM_OUT_OF_RANGE_ERR]}")
            else:
                if value not in cond: # check the value is in a list/tuple
                    raise ValueError(f"Error code {PARAM_INVALID_ERR:x}: {error_message[PARAM_INVALID_ERR]}")
            return
        except Exception as e:
            print(e)


    def write(self, cmd):
        self.instr.write(cmd)
    
    def write_binary_values(self, cmd):
        self.instr.write_binary_values(cmd)
    
    def read(self, cmd):
        return self.instr.read(cmd).rstrip()
    
    def query(self, cmd):
        return self.instr.query(cmd).rstrip()
    
    def query_float(self, cmd):
        return float(self.instr.query(cmd).rstrip())
    
    def query_binary_values(self, cmd):
        return self.instr.query_binary_values(cmd, is_big_endian=False)
    
    def get_idn(self):
        return self.query("*IDN?")

    def reset(self):
        self.write("*RST")

    def clear(self):
        self.write("*CLS")

    def opc(self):
        return self.query("*OPC?")

    @property
    def identity(self):
        return self._identity
    
    @property
    def address(self):
        return self._addr
    
    @property
    def rm(self):
        return self._rm
    

    def __get_name(self):
        return self.__class__.__name__
    
    def __str__(self):
        return f"Instrument: {self.__get_name()} "
    
    def __repr__(self):
        return f"{self.__get_name()}({self.instr, self.identity})"

    


class BasePAS(object):
    """
    A base Photonics Application Suite class

    Parameters
    ----------
    server_addr: str
        The address of the software
    """
    def __init__(self, server_addr):
        self.engine_mgr = win32com.client.Dispatch(server_addr)
        self.engine = self.engine_mgr.NewEngine()
        self.activate()
        activating = 0
        start = time.time()

        # If the engine is not activated 
        while activating == 0:
            time.sleep(0.5) 
            activating = self.engine_status()
            if time.time() - start > 30:
                logging.error("Timeout error: check devices connection")

    def activate(self):
        self.engine.Activate()

    def deactivate(self):
        self.engine.DeActivate()

    def engine_status(self):
        return self.engine.Active
    
    def quit(self):
        self.deactivate()
        self.engine_mgr.DeleteEngine(self.engine)

    def validate_settings(self):
        self.engine.ValidateSettings()

    def __get_name(self):
        return self.__class__.__name__
    
    def __str__(self):
        return f"Photonics Application Suite: {self.__get_name()} "
    
    def __repr__(self):
        return f"{self.__get_name()}({self.engine, self.identity})"


class BaseSweeps(object):
    """
    A base sweep class

    Parameters
    ----------
    instr: an instrument class
        This is the instrument that is used in the sweep
    """
    def __init__(self, instr):
        self.instr = instr

    def __get_name(self):
        return self.__class__.__name__
    
    def __str__(self):
        return f"Sweep: {self.__get_name()} "
    
    def __repr__(self):
        return f"{self.__get_name()}({self.dev})"
    
