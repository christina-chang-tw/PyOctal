from lib.util.util import get_config_dirpath
from lib.util.plot import PlotGraphs

import yaml
from scipy.signal import savgol_filter

def savgol_filter_of_my_own():
    pass



if __name__ == "__main__":

    config_fpath= f'{get_config_dirpath()}/plot_config.yaml'

    with open(config_fpath, 'r') as file:
        configs = yaml.safe_load(file)
    plot = PlotGraphs(configs)

    func = getattr(plot, configs["func"])
    
    func()