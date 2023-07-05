from lib.multimeter import M_8163B

class PASSIVE_TESTING:
    def __init__(self, multimeter: M_8163B):
        self.multimeter = multimeter

    def wavelength_sweep(self, mode: str="STEP", start: float=1540, stop: float=1570, step: float=5):
        self.multimeter.set_sweep_mode(mode=mode)
        self.multimeter.set_sweep_start_stop(start=start, stop=stop)
        self.multimeter.set_sweep_state(state=1)
        self.multimeter.set_sweep_step(step=step)

        
