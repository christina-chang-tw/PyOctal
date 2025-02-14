from pyvisa import ResourceManager
from typing import Union, List, Tuple
import textwrap
import logging

from pyoctal.utils.error import (
    error_message,
    RESOURCE_CLASS_UNKNOWN_ERR,
    RESOURCE_ADDR_UNKNOWN_ERR,
    COND_INVALID_ERR,
    PARAM_OUT_OF_RANGE_ERR,
    PARAM_INVALID_ERR,
    INSTR_NOT_EXIST
)

logger = logging.getLogger(__name__)

class DeviceID:
    """
    Device identity.

    This splits up the return IDN*? query string into a nice format where the user
    can easily access information about the vendor, model number, serial number,
    and the version.

    e.g.
        dev = DeviceID(identity)
        dev.vendor -> vendor information
        dev.serialno -> device serial number
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

    def __eq__(self, other):
        """ Compare equality. """
        if not isinstance(other, DeviceID):
            return NotImplemented
        return self.__dict__ == other.__dict__

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


class BaseInstrument:
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
    def __init__(self, rm: ResourceManager, **kwargs):
        # Communicate with the resource and identify it
        self._addr = None
        self._rm = rm
        self._rm.timeout = 25e+03
        # check which type of resources it is connecting to and automatically determine the read and write termination
        # character based on the resource address
        self._write_termination = kwargs.get("write_termination", "\n")
        self._read_termination = kwargs.get("read_termination", "\n")


    def connect(self, addr: str=None):
        """ Establishing a connection to the device. """
        self._addr = addr
        if self._addr.startswith("ASRL"):
            self._read_termination = "\r\n"
        if addr in self.list_resources(): # Checking if the resource is available
            self._instr = self._rm.open_resource(self._addr)
            self._instr.read_termination = self._read_termination
            self._instr.write_termination = self._write_termination
            instr_type = self._instr.resource_info[3][:4]

            known_type = ("ASRL", "GPIB", "USB", "PXI", "VXI", "TCPIP")

            # make sure that we know the device type
            if instr_type not in known_type:
                raise ValueError(f"Error code {RESOURCE_CLASS_UNKNOWN_ERR:x}: \
                                {error_message[RESOURCE_CLASS_UNKNOWN_ERR]}")
            self._identity = self.get_idn()
        else:
            raise ValueError(f"Error code {RESOURCE_ADDR_UNKNOWN_ERR:x}: \
                            {error_message[RESOURCE_ADDR_UNKNOWN_ERR]}")


    def list_resources(self):
        return self._rm.list_resources()

    @staticmethod
    def value_check(value, cond: Union[Tuple, List]=None):
        """ Check if the value meets the condition. """
        if cond is None: # nothing to check for
            pass
        elif not (isinstance(cond, Union[Tuple, List]) and all(cond)): # the condition is incorrectly set and they are of the same type
            raise ValueError(f"Error code {COND_INVALID_ERR:x}: {error_message[COND_INVALID_ERR]}")
        elif len(cond) == 2 and all(isinstance(n, Union[float, int]) for n in cond):
            if not cond[0] < value < cond[1]: # check the value is within range
                raise ValueError(f"Error code {PARAM_OUT_OF_RANGE_ERR:x}: \
                                 {error_message[PARAM_OUT_OF_RANGE_ERR]}.\n \
                                 Need to be between {cond[0]} and {cond[1]}.")
        else:
            if value not in cond: # check the value is in a List/Tuple
                raise ValueError(f"Error code {PARAM_INVALID_ERR:x}: \
                                 {error_message[PARAM_INVALID_ERR]}.\n \
                                 \nPlease select one of the values: {[', '.join(val) for val in cond]}")


    def write(self, cmd):
        """ Write a command. """
        self._instr.write(cmd)

    def write_binary_values(self, cmd, **kwargs):
        """ Write a command that sets a List of binary values. """
        self._instr.write_binary_values(cmd, **kwargs)

    def query(self, cmd) -> str:
        """ Query command. """
        return self._instr.query(cmd).rstrip()

    def query_bool(self, cmd) -> bool:
        """ Convert the value return from a query to boolean. """
        return bool(self._instr.query(cmd).rstrip())

    def query_int(self, cmd) -> int:
        """ Convert the value return from a query to int. """
        return int(self._instr.query(cmd).rstrip())

    def query_float(self, cmd) -> float:
        """ Convert the value return from a query to float. """
        return float(self._instr.query(cmd).rstrip())

    def query_binary_values(self, cmd, *args, **kwargs) -> List:
        """ Convert the value return from a query to binary values. """
        return self._instr.query_binary_values(cmd, is_big_endian=False, *args, **kwargs)

    def get_idn(self) -> DeviceID:
        """ Get the identity string and parsed by DeviceID class. """
        return DeviceID(self.query("*IDN?"))

    def reset(self):
        """ Reset the instrument. """
        self.write("*RST")

    def clear(self):
        """ Clear the instrument. """
        self.write("*CLS")

    def opc(self) -> bool:
        return self.query("*OPC?")

    def err(self) -> str:
        """ Query of any error has occured. """
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

    @property
    def instr(self):
        return self._instr

    def __get_name(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return f"Instrument: {self.__get_name()} "

    def __repr__(self) -> str:
        return f"{self.__get_name()}({self._instr, self.identity})"


class BaseSweeps:
    """
    A base sweep class.

    Parameters
    ----------
    addrs: List, Tuple, str
        All instrument addresses that need to be connected
    rm:
        Pyvisa resource manager
    folder: str
        Folder name
    fname: str
        Filename 
    """
    def __init__(self, addrs: Union[Tuple,List,str], rm, folder: str, fname: str):
        self._rm = rm
        self._addrs = addrs
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
        """ Check if all instruments needed for a test are present. """
        if isinstance(match, str) and match not in addr_list:
            raise Exception(f"Error code {INSTR_NOT_EXIST:x}: \
                            {error_message[INSTR_NOT_EXIST]}")
        elif isinstance(match, Union[Tuple, List]) and not all([dev_type in addr_list for dev_type in match]):
            raise Exception(f"Error code {INSTR_NOT_EXIST:x}: \
                            {error_message[INSTR_NOT_EXIST]}")


    @classmethod
    def get_callable_funcs(cls):
        """ Get all callable functions from this class. """
        method_list = [method for method in dir(cls) if method.startswith('__') is False or method.startswith('_') is False]

        # filter out specific ones
        method_list = filter(lambda x: x.startswith("run_"), method_list)
        return method_list
