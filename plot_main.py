# Perform version check before everything
from lib.util.util import pyversion_check
pyversion_check()

from lib.util.plot import PlotGraphs
from lib.util.util import get_config_dirpath

import yaml
from pprint import pprint

def main():
    config_fpath= f'{get_config_dirpath()}/plot_config.yaml'

    with open(config_fpath, 'r') as file:
        configs = yaml.safe_load(file)

    folders = [", ".join(i) for i in configs["folders"]] if (len(configs["folders"]) > 1) else configs["folders"][0]
    print("--------------------------------------")
    print(f'{"Folders":10}: {folders}')
    print(f'{"Filename":10}: {configs["fname"]}')
    print(f'{"Function":10}: {configs["func"]}')
    print("--------------------------------------")

    plot = PlotGraphs(configs)

    func = getattr(plot, configs["func"])
    
    func()
    plot.show()


if __name__ == "__main__":
    main()

    
    