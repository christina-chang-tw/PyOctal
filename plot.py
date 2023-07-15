from lib.analysis.plt import PlotGraphs
import matplotlib.pyplot as plt

# The folder names under results folder that you want to inspect
CHIPS = ("KTN_3","KTN_4", "KTN_5") 

# The columns that you want to exclude when plotting IL
# against length of the waveguides
COLUMNS_DROPPING = { 
    # Do not forget the space in front of the number to distinguish
    # between 40.0 and 240.0, etc
    "KTN_3" : (" 40.0", " 160.0"), 
    "KTN_4" : (),
    "KTN_5" : (),
}

# The columns that you want to plot for IL against wavelengths
COLUMNS_PLOT = {
    "KTN_3" : (" 0.0",), 
    "KTN_4" : (" 0.0",),
    "KTN_5" : (),
}

if __name__ == "__main__":

    plot = PlotGraphs()
    
    # e.g. unit = mm: insertion loss [dB/mm]
    plot.plt_len_loss(chips=CHIPS, columns_dropping=COLUMNS_DROPPING, unit="mm")
    plot.plt_lambda_loss(chips=CHIPS, columns_plot=COLUMNS_PLOT, unit="mm")

    plt.legend(loc="upper right")
    plt.minorticks_on()
    plt.show()