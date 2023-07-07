from lib.instruments.pal import PAL

class PASSIVE_TESTING:
    def __init__(self, dev: PAL):
        self.dev = dev
        dev.activate()

    def wavelength_sweep(self, mode: str="STEP", start: float=1540, stop: float=1570, step: float=5):
        self.dev.set_sweep_mode(mode=mode)
        self.dev.set_sweep_start_stop(start=start, stop=stop)
        self.dev.set_sweep_state(state=1)
        self.dev.set_sweep_step(step=step)

        
