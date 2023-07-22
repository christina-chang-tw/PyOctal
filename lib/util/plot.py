from lib.util.file_operations import get_result_dirpath, get_dataframe_from_csv, get_dataframe_from_excel
from lib.analysis.iloss import iloss_coeffs
from lib.util.file_operations import export_to_csv, export_to_excel

import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
from collections import deque

class RealTimePlot(object):
    """
    Plot a live graph.

    Parameters
    ----------
    max_entries: int
        Set the initial maximum entries of the axes of the plot. The axes scales will later on
        be automatically changed
    """

    def __init__(self, max_entries: int=500):
        _, ax = self.__get_new_figure()
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.ax = ax
        self.lineplot, = ax.plot([], [], "-")
        self.ax.get_autoscaley_on()

    @staticmethod
    def __get_new_figure():
        _, ax = plt.subplots()
        ax.grid(which='major', color='#DDDDDD', linewidth=0.8)
        ax.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
        ax.minorticks_on()
        ax.grid(True)
        return ax
    
    @staticmethod
    def show():
        plt.show()

    @staticmethod
    def pause(period):
        plt.pause(period)

    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)
        self.lineplot.set_data(self.axis_x, self.axis_y)
        self.ax.set_xlim(self.axis_x[0], self.axis_x[-1] + 1e-15)
        self.ax.relim(); self.ax.autoscale_view() # rescale the y-axis

    def animate(self, figure, callback, interval = 50):
        import matplotlib.animation as animation
        def wrapper(frame_index):
            self.add(*callback(frame_index))
            self.axes.relim(); self.axes.autoscale_view() # rescale the y-axis
            return self.lineplot
        animation.FuncAnimation(figure, wrapper, interval=interval)
    

class PlotGraphs(object):
    """
    Plot a graph for post-data processing usage.

    Parameters
    ----------
    configs: dict
        This dictionary contains all parameters read in from the configuration file.
    """

    coeffs_name = "iloss_coeffs"
    data_name = "iloss_data"
    info_name = "iloss_info"

    def __init__(self, configs):
        self.structure = configs["structure"]
        self.unit = configs["unit"]
        self.folders = configs["folders"]

    @staticmethod
    def __get_new_figure():
        fig = plt.figure()
        ax = fig.add_axes([0.1,0.1,0.8,0.8])
        ax.grid(which='major', color='#DDDDDD', linewidth=0.8)
        ax.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
        ax.minorticks_on()
        ax.grid(True)
        return ax

    @staticmethod
    def show():
        plt.show()

    @staticmethod
    def get_avgdata(df: pd.DataFrame, avg_range: float, target_lambda):
        upper_lambda = target_lambda + avg_range/2
        lower_lambda = target_lambda - avg_range/2
        upper_rindex = (df['Wavelength'] - upper_lambda).abs().argsort()[:1].values[0]
        lower_rindex = (df['Wavelength'] - lower_lambda).abs().argsort()[:1].values[0]

        # get the row mean and remove the wavelength data
        df_avg = df.iloc[lower_rindex:upper_rindex, :].mean(axis=0).values[1:]
        return df_avg

    def plot_data(self, xdata, ydata, xlabel: str="XXX", ylabel: str="YYY", title: str="Empty Title", typ: str="line"):
        ax = self.__get_new_figure()
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        if typ == "line":
            ax.plot(xdata, ydata)
        elif typ == "scatter":
            ax.scatter(xdata, ydata)
        else
            raise RuntimeError("Invalid plot type")

    def plt_len_loss_csv(self, configs):

        exp_lambda = configs["exp_lambda"]
        avg_range = configs["lambda_avgrange"]

        ax = self.__get_new_figure()
        ax.set_xlabel(f'Length [{self.unit}]')
        ax.set_ylabel(f'Loss [dB/{self.unit}]')
        ax.set_title('Insertion Loss of Different Chips')

        for name in self.folders:
            df_coeff = []

            df = get_dataframe_from_csv(path=get_result_dirpath(name), fname=f'{self.structure}_{self.data_name}')
            info = get_dataframe_from_csv(path=get_result_dirpath(name), fname=f'{self.structure}_{self.info_name}')

            no_channels = int(info.loc[info["Params"] == "Number of channels"].loc[:,"Value"])

            if configs["columns_drop"][name] is not None:
                df = df.loc[:, [not x for x in df.columns.str.endswith(tuple(configs["columns_drop"][name]))]]

            for i in range(no_channels):
                label = f'{name}' if no_channels == 1 else f'{name}_CH{i}'
                temp = df.loc[:, df.columns.str.startswith(f'CH{i}')]

                xdata = [float(i.split(" - ")[1]) for i in temp.columns.values[0:]]
                ydata = self.get_avgdata(df=df, avg_range=avg_range, target_lambda=exp_lambda)

                # linear regression
                fit = np.polyfit(xdata, ydata, deg=1)
                xline = np.linspace(min(xdata), max(xdata))
                yline = xline*fit[0] + fit[1]

                ax.plot(xline, yline, ':')
                ax.scatter(xdata, ydata, label=label)
                print(f'{name}_CH{i} : y = {round(fit[0],4)}x {round(fit[1],4)}')
                df_coeff = iloss_coeffs(df=temp, wavelengths=df['Wavelength'], lengths=xdata, no_channels=no_channels, unit=self.unit)
            
            export_to_csv(data=df_coeff, path=get_result_dirpath(name), fname=f'{self.structure}_iloss_coeffs')
        ax.legend(fontsize=8)

    

    def plt_lambda_loss(self, configs):
        
        ax = self.__get_new_figure()
        ax.set_xlabel(f'Wavelength [nm]')
        ax.set_ylabel(f'Loss [dB/{self.unit}]')
        ax.set_title('Insertion Loss of Different Wavelengths')

        for name in self.folders:

            df = get_dataframe_from_csv(path=get_result_dirpath(name), fname=f'{self.structure}_{self.data_name}')
            info = get_dataframe_from_csv(path=get_result_dirpath(name), fname=f'{self.structure}_{self.info_name}')

            no_channels = int(info.loc[info["Params"] == "Number of channels"].loc[:,"Value"])
            if configs["columns_plot"][name] is not None:
                df = df.loc[:, [x for x in df.columns.str.endswith(tuple(configs["columns_plot"][name]))]]

            xdata = df['Wavelength']

            for i in range(no_channels):
                temp = df.loc[:, df.columns.str.startswith(f'CH{i}')]
                
                for length in temp.columns.values:
                    label = f'{name}_{length.split(" - ")[1]}{self.unit}' if no_channels == 1 else f'{name}_{length}{self.unit}'
                    ydata = temp.loc[:,length]
                    ax.plot(xdata, ydata, label=label)
        ax.legend(fontsize=8)


    def plt_coeffs(self, _):
        
        ax1= self.__get_new_figure()
        ax1.set_xlabel(f'Wavelength [nm]')
        ax1.set_ylabel(f'Loss [dB/{self.unit}]')
        ax1.set_title('Waveguide Loss of Different Wavelengths')

        ax2 = self.__get_new_figure()
        ax2.set_xlabel(f'Wavelength [nm]')
        ax2.set_ylabel(f'Insertion Loss [dB]')
        ax2.set_title('Insertion Loss of Different Wavelengths')

        for name in self.folders:

            df_coeffs = get_dataframe_from_csv(path=get_result_dirpath(name), fname=f'{self.structure}_{self.coeffs_name}')
            info = get_dataframe_from_csv(path=get_result_dirpath(name), fname=f'{self.structure}_{self.info_name}')
            
            no_channels = int(info.loc[info["Params"] == "Number of channels"].loc[:,"Value"])
            xdata = df_coeffs['Wavelength']

            for i in range(no_channels):
                label = f'{name}' if no_channels == 1 else f'{name}_CH{i}'
                ax1.plot(xdata, df_coeffs[f'CH{i} - loss [db/{self.unit}]'], label=label)
                ax2.plot(xdata, df_coeffs[f"CH{i} - insertion loss [dB]"], label=label)

        ax1.legend(fontsize=8)
        ax2.legend(fontsize=8)



    def plt_len_loss_excel(self, configs):

        exp_lambda = configs["exp_lambda"]

        ax = self.__get_new_figure()
        ax.set_xlabel(f'Length [{self.unit}]')
        ax.set_ylabel(f'Loss [dB/{self.unit}]')
        ax.set_title('Insertion Loss of Different Chips')

        for name in self.folders:

            df, info = get_dataframe_from_excel(path=get_result_dirpath(name), fname=f'{self.structure}_{self.data_name}', sheet_names=configs["sheets"])
            for sheet in configs["sheets"]:
                df_dropped = df[sheet]
                df_coeff = []

                no_channels = int(info.loc[info["General:"] == "NumberOfChannels"].loc[:, "Unnamed: 1"])
                if configs["columns_drop"][name] is not None:
                    df_dropped = df_dropped.loc[:, [not x for x in df_dropped.columns.str.endswith(tuple(configs["columns_drop"][name]))]]

                wavelength = df_dropped['Wavelength']*1e+09

                for i in range(no_channels):
                    label = f'{name}_{sheet}' if no_channels == 1 else f'{name}_{sheet}_CH{i}'
                    temp = df_dropped.loc[:, df_dropped.columns.str.startswith(f'CH{i}')]
           
                    xdata = [float(i.split(" - ")[1]) for i in temp.columns.values[0:]]
                    ydata = temp.iloc[(wavelength - exp_lambda).abs().argsort()[:1]].values[0][0:]

                    # linear regression
                    fit = np.polyfit(xdata, ydata, deg=1)
                    xline = np.linspace(min(xdata), max(xdata))
                    yline = xline*fit[0] + fit[1]

                    ax.plot(xline, yline, ':')
                    ax.scatter(xdata, ydata, label=label)
                    offset = f'+{round(fit[1],4)}' if fit[1] > 0 else round(fit[1], 4) if fit[1] < 0 else 0
                    print(f'{name}_CH{i} : y = {round(fit[0],4)}x {offset}')
                    df_coeff = iloss_coeffs(df=temp, wavelengths=wavelength, lengths=xdata, no_channels=no_channels, unit=self.unit)
                
                export_to_excel(data=df_coeff, path=get_result_dirpath(name), fname=f'{self.structure}_iloss_coeffs')
        ax.legend(fontsize=8)


    def plt_lambda_loss_excel(self, configs):
        
        ax = self.__get_new_figure()
        ax.set_xlabel(f'Wavelength [nm]')
        ax.set_ylabel(f'Loss [dB/{self.unit}]')
        ax.set_title('Insertion Loss of Different Wavelengths')

        for name in self.folders:
            
            df, info = get_dataframe_from_excel(path=get_result_dirpath(name), fname=f'{self.structure}_{self.data_name}', sheet_names=configs["sheets"])
            
            for sheet in configs["sheets"]:
                df_dropped = df[sheet]
                
                if configs["columns_drop"][name] is not None:
                    df_dropped = df_dropped.loc[:, [x for x in df_dropped.columns.str.endswith(tuple(configs["columns_plot"][name]))]]

                no_channels = int(info.loc[info["General:"] == "NumberOfChannels"].loc[:, "Unnamed: 1"])
                xdata = df_dropped['Wavelength']*1e+09

                for i in range(no_channels):
                    temp = df_dropped.loc[:, df_dropped.columns.str.startswith(f'CH{i}')]
                    
                    for length in temp.columns.values:
                        label = f'{name}_{length.split(" - ")[1]}{self.unit}' if no_channels == 1 else f'{name}_{length}{self.unit}'
                        ydata = np.negative(temp.loc[:,length])
                        ax.plot(xdata, ydata, label=label)
        ax.legend(fontsize=8)
