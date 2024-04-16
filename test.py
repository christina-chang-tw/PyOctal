def set_detect_avgtime(self, period: float):
    """ Set the detector average time [s]. """
    self.write(f"{self.detect}:power:atime {period}s")

def set_detect_wav(self, wavelength: float):
    """ Set the detector wavelength [nm]. """
    self.write(f"{self.detect}:power:wavelength {wavelength}nm")

def set_detect_prange(self, prange: float):
    """ Set the detector power range [dBm]. """
    self.write(f"{self.detect}:power:range {prange}dBm")

def set_detect_autorange(self, auto: bool):
    """ Set the detector power autorange. """
    self.write(f"{self.detect}:power:range:auto {auto}")

cmds = {
    "detect_avgtime": "{}:power:atime {}",
    "detect_wav": "{}:power:wavelength {}nm",
    "detect_prange": "{}:power:range {}dBm",
    "detect_autorange": "{}:power:range:auto {}",
}

def set(self, cmd, val):
    self.write(cmds[cmd].format(self.detect, val))
