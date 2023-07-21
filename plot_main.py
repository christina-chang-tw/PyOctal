# Check the python version first!
from lib.util.util import version_check
version_check()

from lib.analysis.plt import PlotGraphs
from lib.util.util import get_config_dirpath

import matplotlib.pyplot as plt
import yaml


if __name__ == "__main__":
    config_fpath= f'{get_config_dirpath()}/plot_config.yaml'
    plot = PlotGraphs()

    with open(config_fpath, 'r') as file:
        config = yaml.safe_load(file)

    func = getattr(plot, config["func"])
    
    func(config)

    plt.minorticks_on()
    plt.show()
    