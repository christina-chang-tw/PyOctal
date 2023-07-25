from lib.util.file_operations import get_result_dirpath, get_dataframe_from_csv, get_dataframe_from_excel
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

    def __init__(self, configs):
        self.configs = configs
        self.unit = configs["unit"]
        self.folders = configs["folders"]
        self.no_channels = configs["no_channels"]
        self.fname = configs["fname"]
        self.title = configs["title"]

    @staticmethod
    def __get_new_figure(title):
        """ Obtain a new figure """
        fig = plt.figure()
        ax = fig.add_axes([0.1,0.1,0.8,0.8])
        ax.set_title(title)
        ax.grid(which='major', color='#DDDDDD', linewidth=0.8)
        ax.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
        ax.minorticks_on()
        ax.grid(True)
        return ax

    @staticmethod
    def linear_regression(xdata, ydata):
        fit = np.polyfit(xdata, ydata, deg=1)

        xline = np.linspace(min(xdata), max(xdata))
        yline = xline*fit[0] + fit[1]

        return xline, yline, fit

    @staticmethod
    def show():
        """ Show plots """
        plt.show()

    @staticmethod
    def get_avgdata(df: pd.DataFrame, avg_range: float, target_lambda):
        """ Average the datapoints across a wavelength range for each length """

        if avg_range == 0: # only want a specific wavelength data
            return df.iloc[(df["Wavelength"] - target_lambda).abs().argsort()[:1]].values[0][1:]
        
        upper_lambda = target_lambda + avg_range/2
        lower_lambda = target_lambda - avg_range/2
        upper_rindex = (df["Wavelength"] - upper_lambda).abs().argsort()[:1].values[0]
        lower_rindex = (df["Wavelength"] - lower_lambda).abs().argsort()[:1].values[0]

        # get the row mean and remove the wavelength data
        df_avg = df.iloc[lower_rindex:upper_rindex, :].mean(axis=0).values[1:]
        return df_avg

    def plot_data(self, xdata, ydata, xlabel: str="XXX", ylabel: str="YYY", title: str="Empty Title", typ: str="line"):
        """ Given x and y, plot a graph"""
        ax = self.__get_new_figure()
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        try:
            if typ == "line":
                ax.plot(xdata, ydata)
            elif typ == "scatter":
                ax.scatter(xdata, ydata)
            else:
                raise RuntimeError("Invalid plot type")
        except Exception as error:
            raise error

    def plt_len_loss_csv(self):
        """ Plot a loss v.s. length graph with the data from a csv file """
        exp_lambda = self.configs["exp_lambda"]
        avg_range = self.configs["lambda_avgrange"]
        no_channels = self.no_channels

        ax = self.__get_new_figure(self.title)
        ax.set_xlabel(f'Length [{self.unit}]')
        ax.set_ylabel(f'Loss [dB/{self.unit}]')

        for name in self.folders:
            df_coeff = []

            df = get_dataframe_from_csv(path=get_result_dirpath(name), fname=self.fname)

            # Drop the unwanted lengths
            if self.configs["columns_drop"][name] is not None:
                df = df.loc[:, [not x for x in df.columns.str.startswith(tuple(self.configs["columns_drop"][name]))]]

            for i in range(no_channels):
                label = f'{name}' if no_channels == 1 else f'{name}_CH{i}'

                # obtain the columns from the correct channel
                temp = df.loc[:, df.columns.str.endswith(f'CH{i}')]

                # extract the lengths out of headers
                xdata = [float(i.split(" - ")[0]) for i in temp.columns.values[0:]] 
                # get a loss averaged over a specified wavelength range for each length
                ydata = self.get_avgdata(df=df, avg_range=avg_range, target_lambda=exp_lambda)

                # linear regression
                xline, yline, fit = self.linear_regression(xdata, ydata)

                # plot data
                ax.plot(xline, yline, ':')
                ax.scatter(xdata, ydata, label=label)
                print(f'{name}_CH{i} : y = {round(fit[0],4)}x {round(fit[1],4)}')
            
            export_to_csv(data=df_coeff, path=get_result_dirpath(name), fname=f'{self.fname}_iloss_coeffs')
        ax.legend(fontsize=8)

    

    def plt_lambda_loss(self):
        """ Plot a loss v.s. wavelength graph with the data from a csv file """
        no_channels = self.no_channels

        ax = self.__get_new_figure(self.title)
        ax.set_xlabel(f'Wavelength [nm]')
        ax.set_ylabel(f'Loss [dB/{self.unit}]')

        for name in self.folders:

            df = get_dataframe_from_csv(path=get_result_dirpath(name), fname=self.fname)

            # plot the wanted columns
            if self.configs["columns_plot"][name] is not None:
                df = df.loc[:, [x for x in df.columns.str.startswith(tuple(self.configs["columns_plot"][name]))]]

            xdata = df['Wavelength']

            for i in range(no_channels):
                # obtain the columns from the correct channel
                temp = df.loc[:, df.columns.str.endswith(f'CH{i}')]
                
                for length in temp.columns.values:
                    label = f'{name}_{length.split(" - ")[0]}{self.configs["end_of_legend"]}' if no_channels == 1 else f'{name}_{length}{self.configs["end_of_legend"]}'
                    ydata = temp.loc[:,length]
                    ax.plot(xdata, ydata, label=label)

        ax.legend(fontsize=8)


    # def plt_coeffs(self): (NOT USEFUL)
    #     """ Import from a loss coefficient file and plot the waveguide loss and insertion loss. """
    #     no_channels = self.no_channels

    #     ax1= self.__get_new_figure()
    #     ax1.set_xlabel(f'Wavelength [nm]')
    #     ax1.set_ylabel(f'Loss [dB/{self.unit}]')
    #     ax1.set_title('Waveguide Loss of Different Wavelengths')

    #     ax2 = self.__get_new_figure()
    #     ax2.set_xlabel(f'Wavelength [nm]')
    #     ax2.set_ylabel(f'Insertion Loss [dB]')
    #     ax2.set_title('Insertion Loss of Different Wavelengths')

    #     for name in self.folders:

    #         df_coeffs = get_dataframe_from_csv(path=get_result_dirpath(name), fname=self.fname)
    #         xdata = df_coeffs['Wavelength']

    #         for i in range(no_channels):
    #             label = f'{name}' if no_channels == 1 else f'{name}_CH{i}'
    #             ax1.plot(xdata, df_coeffs[f'CH{i} - loss [db/{self.unit}]'], label=label)
    #             ax2.plot(xdata, df_coeffs[f"CH{i} - insertion loss [dB]"], label=label)

    #     ax1.legend(fontsize=8)
    #     ax2.legend(fontsize=8)



    def plt_len_loss_excel(self):
        """ Plot a loss v.s. length graph with the data from a excel file """
        exp_lambda = self.configs["exp_lambda"]
        avg_range = self.configs["lambda_avgrange"]
        no_channels = self.no_channels

        ax = self.__get_new_figure(self.title)
        ax.set_xlabel(f'Length [{self.unit}]')
        ax.set_ylabel(f'Loss [dB/{self.unit}]')

        for name in self.folders:

            df = get_dataframe_from_excel(path=get_result_dirpath(name), fname=self.fname, sheet_names=self.configs["sheets"])
            
            for sheet in self.configs["sheets"]:
                df_dropped = df[sheet]
                df_coeff = []

                # Drop the unwanted lengths
                if self.configs["columns_drop"][name] is not None:
                    df_dropped = df_dropped.loc[:, [not x for x in df_dropped.columns.str.startswith(tuple(self.configs["columns_drop"][name]))]]
                
                df_dropped["Wavelength"] = df_dropped['Wavelength']*1e+09 # make sure that wavelength is in nm

                for i in range(no_channels):
                    label = f'{name}_{sheet}' if no_channels == 1 else f'{name}_{sheet}_CH{i}'
                    
                    # obtain the columns from the correct channel
                    temp = df_dropped.loc[:, df_dropped.columns.str.endswith(f'CH{i}')]
                    
                    # extract the lengths out of headers
                    xdata = [float(i.split(" - ")[0]) for i in temp.columns.values[0:]] # get the lengths from the header
                    # get a loss averaged over a specified wavelength range for each length
                    ydata = self.get_avgdata(df=df_dropped, avg_range=avg_range, target_lambda=exp_lambda) # get the average data

                    # linear regression
                    xline, yline, fit = self.linear_regression(xdata, ydata)

                    # plot data
                    ax.plot(xline, yline, ':')
                    ax.scatter(xdata, ydata, label=label)
                    offset = f'+{round(fit[1],4)}' if fit[1] > 0 else round(fit[1], 4) if fit[1] < 0 else 0
                    print(f'{name}_CH{i} : y = {round(fit[0],4)}x {offset}')
                    df_coeff = iloss_coeffs(df=temp, wavelengths=df_dropped["Wavelength"], lengths=xdata, no_channels=no_channels, unit=self.unit)
                
                export_to_excel(data=df_coeff, path=get_result_dirpath(name), fname=f'{self.fname}_iloss_coeffs')
        ax.legend(fontsize=8)


    def plt_lambda_loss_excel(self):
        """ Plot a loss v.s. wavelength graph with the data from a excel file """
        no_channels = self.no_channels

        ax = self.__get_new_figure(self.title)
        ax.set_xlabel(f'Wavelength [nm]')
        ax.set_ylabel(f'Loss [dB/{self.unit}]')

        for name in self.folders:
            
            df = get_dataframe_from_excel(path=get_result_dirpath(name), fname=self.fname, sheet_names=self.configs["sheets"])
            
            for sheet in self.configs["sheets"]:
                df_dropped = df[sheet]
                
                # plot the wanted columns
                if self.configs["columns_drop"][name] is not None:
                    df_dropped = df_dropped.loc[:, [x for x in df_dropped.columns.str.startswith(tuple(self.configs["columns_plot"][name]))]]

                xdata = df_dropped['Wavelength']*1e+09

                for i in range(no_channels):
                    # obtain the columns from the correct channel
                    temp = df_dropped.loc[:, df_dropped.columns.str.endswith(f'CH{i}')]
                    
                    for length in temp.columns.values:
                        label = f'{name}_{length.split(" - ")[0]}{self.configs["end_of_legend"]}' if no_channels == 1 else f'{name}_{length}{self.configs["end_of_legend"]}'
                        ydata = np.negative(temp.loc[:,length])
                        ax.plot(xdata, ydata, label=label)
        ax.legend(fontsize=8)
