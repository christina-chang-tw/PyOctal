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
        self.addr = rsc_addr
        self.rm = pyvisa.ResourceManager()
        self.rm.timeout = 20000
        self.rm.read_termination = termination
        
        if rsc_addr in self.rm.list_resources(): # Checking if the resource is available
            self.instr = self.rm.open_resource(rsc_addr)
            if self.inst.resource_info[3][:4] == 'ASRL':
                #This should be changed! gpib is also a instrument type
                if termination is not None:
                    self.inst.read_termination = termination
                    self.inst.write_termination = termination
                print('You have connected succesfully with an ASRL type resource')
            elif self.inst.resource_info[3][:4] == 'GPIB':
                print('You have connected succesfully with an GPIB type resource')
            elif self.inst.resource_info[3][:4] == 'USB0':
                print('You have connected succesfully with an USB0 type resource')
            else:
                raise Exception('Resource class not contemplated, check pyLab library')
            self.identify = self.inst.query("*IDN?")

        else:
            raise Exception("Resource not know, check your ports or NI MAX")
        
    def write(self, str):
        return self.instr.write(str)
    
    def read(self, str):
        return self.instr.read(str).rstrip()
    
    def query(self, str):
        return self.instr.query(str).rstrip()
    
    def get_idn(self):
        return self.query("*IDN?")

    def reset(self):
        self.write("*RST")


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

