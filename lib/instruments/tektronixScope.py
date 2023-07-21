from lib.base import BaseInstrument

import numpy
import matplotlib.pyplot as plot


class TektronixScope(BaseInstrument):
    """Class to control a Tektronix series oscilloscope"""
    def __init__(self, addr):
        super().__init__(rsc_addr=addr)
        self.name = self.get_idn()
        self.set_data_format(format="asci")

    def set_scope_acq_state(self, state: bool=1):
        self.write(f"acquire:state {state}")

    # Measurement
    def set_meas_source(self, src: str):
        self.write(f"measurement:immed:source {src}")
    
    def set_meas_type(self, typ: str):
        self.write(f"measurement:immed:type {typ}")

    def get_meas_data(self):
        return self.query("measurement:immed:value?")

    # Wfmoutpre
    def get_wfmo_ymult(self):
        # get voltage scale
        return self.query_float("wfmoutpre:ymult?")
    
    def get_wfmo_yoff(self):
        # get voltage offset
        return self.query_float("wfmoutpre:yoff?")
    
    def get_wfmo_yzero(self):
        # get voltage zero
        return self.query_float("wfmoutpre:yzero?")
    
    # Wfmp
    def get_wfmp_ymult(self, src: str):
        # get voltage scale
        return self.query_float(f"wfmp:{src}:ymult?")
    
    def get_wfmp_yoff(self, src: str):
        # get voltage offset
        return self.query_float(f"wfmp:{src}:yoff?")
    
    def get_wfmp_yzero(self, src: str):
        # get voltage zero
        return self.query_float(f"wfmp:{src}:yzero?")
    
    def get_wfmp_xunit(self):
        return self.query("wfmp:xunit?")
    
    def get_wfmp_yunit(self):
        return self.query("wfmp:yunit?")
    
    def get_wfmp_units(self):
        return self.get_wfmp_xunit(), self.get_wfmp_yunit()

    # Horizontal
    def get_horizontal_recordlength(self):
        return int(self.query("horizontal:recordlength?"))
    
    def get_horizontal_scale(self):
        return self.query_float("horizontal:main:scale?")
    
    def get_horizontal_pos(self):
        # get timescale offset
        return self.query_float("horizontal:main:position?")
    

    # Data
    def set_data_format(self, format: str="asci"):
        if format.lower() not in ("asci", "rib", "rpb", "fpb", "sri", "srp", "sfp"):
            raise RuntimeError("Bad value")
        self.write(f"data:encdg {format}")

    def set_data_source(self, src: str):
        self.write(f"data:source {src}")

    def get_curve(self):
        return self.query("curve?")

    def read_data(self):
        """ Function for reading data and parsing binary into numpy array """
        data = self.get_curve()
        datasplit = data.split(',')
        dataint = list(map(int,datasplit))

        # First few bytes are characters to specify
        # the length of the transmission. Need to strip these off:
        # we'll assume a 5000-byte transmission
        # so the string would be "#45000" and we therefor strip 6 bytes.
        # return numpy.frombuffer(rawdata[6:-1], 'i2')
        return numpy.array(dataint)


    def get_data(self,source):
        """
        Get scaled data from source where source is one of
        CH1,CH2,REFA,REFB
        """

        self.set_data_source(source)
        data = self.read_data()

        # Get the voltage scale
        ymult = self.get_wfmp_ymult(source)

        # And the voltage offset
        yoff = self.get_wfmp_yoff(source)

        # And the voltage zero
        yzero = self.get_wfmp_yzero(source)

        data = ((data - yoff) * ymult) + yzero
        return data

    def get_xdata(self):
        """Method to get the horizontal data array from a scope"""
        # Get the timescale
        timescale = self.get_horizontal_scale()

        # Get the length of the horizontal record
        time_size = self.get_horizontal_recordlength()

        time = numpy.arange(0,timescale*10,timescale*10/time_size)
        return time


    def plot_wfm(self, source):
        "Method to plot the oscilloscope waveform"
        x = self.get_xdata()
        y = self.get_data(source)
        xunit, yunit = self.get_wfmp_units()

        plot.xlabel("Time " + xunit)
        plot.ylabel("Voltage " + yunit)
        plot.plot(x,y)
        plot.show()


    def get_mean(self, source):
        "Method to get the waveform mean using the oscilloscope measure function"

        #Set the measurement source and type
        self.set_meas_source(source)
        self.set_meas_type(typ="Mean")

        return self.get_meas_data()