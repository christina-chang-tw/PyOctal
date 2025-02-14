from typing import List

from pyvisa import ResourceManager

from pyoctal.instruments.base import BaseInstrument

class NicsLabXPOW(BaseInstrument):
    """
    NICS Lab XPOW Power Meter VISA Library.

    Parameters
    ----------
    addr: str
        The address of the instrument
    rm:
        Pyvisa resource manager
    """

    def __init__(self, rm: ResourceManager):
        super().__init__(rm=rm)
        self.max_curr = 300
        self.max_volt = 29
        self.channel_number = 8

    @property
    def max_current(self):
        return self.max_curr

    @property
    def max_voltage(self):
        return self.max_volt

    def cvcali_single(self, chan: int, volt: float):
        """ Calibrate a single channel. """
        self.write(f"CH:{chan}:CALIB:{volt}")

    def cvcali_all(self, volts: List):
        """ Calibrate all channels. """
        for chan in range(self.channel_number):
            self.cvcalibrate_single(chan+1, volts[chan])

    def set_volt_single(self, chan: int, volt: float):
        """ Set the laser voltage [V]. """
        self.write(f"CH:{chan}:VOLT:{volt}")

    def set_volt_all(self, volts: List):
        """ Set the laser voltage [V] for all channels. """
        for chan in range(self.channel_number):
            self.set_volt_single(chan+1, volts[chan])

    def set_group_volt(self, chmin: int, chmax: int, volt: float):
        " Set output voltage for a group of channels. "
        self.write(f"CH:{chmin}-{chmax}:{volt}")

    def set_range_all(self, ranges: List):
        for chan in range(self.channel_number):
            self.write(f"CH:{chan+1}:SVR:{ranges[chan]}")


    def set_curr_single(self, chan: int, curr: float):
        """ Set the laser voltage [V]. """
        self.write(f"CH:{chan}:CURR:{curr}")


    def set_curr_all(self, currs: List):
        """ Set the laser voltage [V] for all channels. """
        for chan in range(self.channel_number):
            self.set_curr_single(chan+1, currs[chan])

    def set_channel(self, chan: int, volt: float, curr: float):
        """ Set a channel's current and voltage. """
        self.set_volt_single(chan, volt)
        self.set_curr_single(chan, curr)


    def read_channel_data(self, chan: int):
        """ Get the real time voltage [V] current [A]. """
        result = self.query(f"CH:{chan}:VAL?")
        results = result.split(':')

        # third and fourth elements wil be voltage and current
        return float(results[2]), float(results[3])

    def set_gpio_state(self, pin: int, state: str):
        """ Set the GPIO state. """
        self.write(f"GPIO:PD{pin}:{state}")

    def set_measurement_config(self, t_volt_conv: float, t_curr_conv: float, avg_pts: int):
        """ 
        Set the measurement configurations.
        
        Parameters
        ----------
        t_volt_conv: float
            Voltage measurement conversion time (us)
        t_curr_conv: float
            Current measurement conversion time (us)
        avg_pts: int
            Count of samples to be averaged.
        """
        self.write(f"MEASCONF:{t_volt_conv*1E-06}:{t_curr_conv*1E-06}:{avg_pts}")
