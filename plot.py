from lib.analysis.plt import PlotGraphs
from lib.util.file_operations import get_config_dirpath

import matplotlib.pyplot as plt
import yaml

config_fpath= f'{get_config_dirpath()}/plot_config.yaml'


if __name__ == "__main__":
    with open(config_fpath, 'r') as file:
        config = yaml.safe_load(file)

    plot = PlotGraphs()
    
    # e.g. unit = mm: insertion loss [dB/mm]
    # plot.plt_len_loss_csv(chips=config["folders"], structure=config["structure"], columns_dropping=config["columns_dropping"], unit="mm")
    # plot.plt_lambda_loss(chips=config["folders"], structure=config["structure"], columns_plot=config["columns_plot"], unit="mm")

    #plot.plt_len_loss_excel(chips=config["folders"], structure=config["structure"], columns_dropping=config["columns_dropping"], sheet_names=config["sheets"], unit="mm")
    plot.plt_lambda_loss_excel(chips=config["folders"], structure=config["structure"], columns_plot=config["columns_plot"], sheet_names=config["sheets"], unit="mm")

    plt.minorticks_on()
    plt.show()
    