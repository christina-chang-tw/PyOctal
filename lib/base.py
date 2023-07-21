import win32com.client
import pyvisa
import time

import logging

logger = logging.getLogger(__name__)

def list_resources():
    """Function that prints and returns a list with all the available resources in the PC. Needs the visa library from NI"""
    # List of the available resources
    resources = pyvisa.ResourceManager().list_resources()
    print('Available resources in the PC:')
    print(resources)
    return resources

class BaseInstrument(object):

    def __init__(self, rsc_addr, termination: str='\n'):
        # Communicate with the resource and identify it
        self._addr = rsc_addr
        self._rm = pyvisa.ResourceManager()
        self._rm.timeout = 20000
        self._rm.read_termination = termination
        
        # Connect to the device
        if rsc_addr in self._rm.list_resources(): # Checking if the resource is available
            self.instr = self._rm.open_resource(rsc_addr)
            if self.instr.resource_info[3][:4] == 'ASRL':
                #This should be changed! gpib is also a instrument type
                if termination is not None:
                    self.instr.read_termination = termination
                    self.instr.write_termination = termination
                print('You have connected succesfully with an ASRL type resource')
            elif self.instr.resource_info[3][:4] == 'GPIB':
                print('You have connected succesfully with an GPIB type resource')
            elif self.instr.resource_info[3][:4] == 'USB0':
                print('You have connected succesfully with an USB0 type resource')
            else:
                raise Exception('Resource class not contemplated, check pyLab library')
        
            self._identity = self.get_idn()
        
        else:
            raise Exception("Resource not know, check your ports or NI MAX")
        
        
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
    def __init__(self, instr):
        self.instr = instr

    def __get_name(self):
        return self.__class__.__name__
    
    def __str__(self):
        return f"Sweep: {self.__get_name()} "
    
    def __repr__(self):
        return f"{self.__get_name()}({self.dev})"
    
