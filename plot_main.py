# Perform version check before everything
from lib.util.util import pyversion_check
pyversion_check()

from lib.util.plot import PlotGraphs
from lib.util.util import get_config_dirpath

import yaml


if __name__ == "__main__":
    config_fpath= f'{get_config_dirpath()}/plot_config.yaml'

    with open(config_fpath, 'r') as file:
        configs = yaml.safe_load(file)

    plot = PlotGraphs(configs)

    func = getattr(plot, configs["func"])
    
    func()
    plot.show()

    
    