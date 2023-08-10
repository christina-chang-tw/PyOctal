# Perform version check before everything
from lib.util.util import pyversion_check
pyversion_check()

import yaml
import logging

from lib.util.plot import PlotGraphs
from lib.util.util import get_config_dirpath, setup_rootlogger

LOG_FNAME = "./logging.log"
root_logger = logging.getLogger()
setup_rootlogger(root_logger, LOG_FNAME)
logger = logging.getLogger(__name__)


def main():
    config_fpath= f'{get_config_dirpath()}/plot_config.yaml'

    with open(file=config_fpath, mode='r') as file:
        configs = yaml.safe_load(file)

    folders = [", ".join(configs["folders"])] if (len(configs["folders"]) > 1) else configs["folders"][0]
    logger.info("--------------------------------------")
    logger.info(f'{"Folders":10}: {folders}')
    logger.info(f'{"Filename":10}: {configs["fname"]}')
    logger.info(f'{"Function":10}: {configs["func"]}')
    logger.info("--------------------------------------")

    plot = PlotGraphs(configs)

    func = getattr(plot, configs["func"])
    func()
    
    plot.show()


if __name__ == "__main__":
    main()

    
    