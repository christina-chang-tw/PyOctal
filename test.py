from lib.util.file_operations import get_dataframe_from_excel
from lib.util.util import get_result_dirpath
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


def filtering(x, y):
    x = np.array(x).reshape(-1,1)
    pf = PolynomialFeatures(3)
    x = pf.fit_transform(x)
    reg = LinearRegression().fit(x, y)
    return reg, x

def filter_signal(th, x, signal):
    f_s = fft_filter(th, x, signal)
    return np.real(np.fft.ifft(f_s))

def fft_filter(perc, x, signal):
    print(signal)
    fft_signal = np.fft.fft(signal)
    ax1 = new_fig()
    ax1.plot(x, fft_signal, label="fft")
    fft_abs = np.abs(fft_signal)
    ax2 = new_fig()
    ax2.plot(x, fft_abs, label="abs")
    print((2*fft_abs[0:int(len(signal)/2.)]/len(x)).max())
    th=perc*(2*fft_abs[0:int(len(signal)/2.)]/len(x)).max()
    fft_tof=fft_signal.copy()
    fft_tof_abs=np.abs(fft_tof)
    fft_tof_abs=2*fft_tof_abs/len(x)
    fft_tof[fft_tof_abs<=th]=0
    return fft_tof

def new_fig():
    fig = plt.figure()
    ax = fig.add_axes([0.1,0.1,0.8,0.8])
    ax.grid(which='major', color='#DDDDDD', linewidth=0.8)
    ax.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
    ax.minorticks_on()
    ax.grid(True)
    return ax


sheets = ("Si waveguide",)
name = "Chip_6"
lengths = (0, 8)


            
df = get_dataframe_from_excel(path=get_result_dirpath(name), fname="KTN_chip", sheet_names=sheets)
    
for sheet in sheets:
    df_dropped = df[sheet]
    xdata = df_dropped.loc[:,'Wavelength']*1e+09


    df_dropped = df_dropped.loc[:, list(df_dropped.columns.str.startswith(tuple(str(lengths))))]

    
    # obtain the columns from the correct channel
    temp = df_dropped.loc[:, df_dropped.columns.str.endswith(f'CH0')]
    temp.columns = [float(t.split(" - ")[0]) for t in temp.columns.values] # replaces the index with only the length
    temp = temp.sort_index(axis=1, ascending=True) # sort out the index in ascending order
    
    ax1 = new_fig()

    for length in lengths:
    
        label = f'{name}_{length}'
        y = temp.loc[:,length]
        ydata = np.negative(y)

        signal = ydata.rolling(window=100).mean()
        
        ax1.plot(xdata, ydata)
        ax1.plot(xdata, signal)





plt.show()