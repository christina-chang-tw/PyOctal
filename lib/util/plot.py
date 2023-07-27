from lib.util.file_operations import get_result_dirpath, get_dataframe_from_csv, get_dataframe_from_excel
from lib.util.file_operations import export_to_csv

import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
from collections import deque
import matplotlib.animation as animation

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
        _, axes = self.__get_new_figure()
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axes = axes
        self.lineplot, = axes.plot([], [], "-")
        self.axes.get_autoscaley_on()

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
        self.axes.set_xlim(self.axis_x[0], self.axis_x[-1] + 1e-15)
        self.axes.relim()
        self.axes.autoscale_view() # rescale the y-axis

    def animate(self, figure, callback, interval = 50):
        def wrapper(frame_index):
            self.add(*callback(frame_index))
            self.axes.relim()
            self.axes.autoscale_view() # rescale the y-axis
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
        df_avg = np.negative(df.iloc[lower_rindex:upper_rindex, :].mean(axis=0).values[1:])
        return df_avg

    def plot_data(self, xdata, ydata, xlabel: str="XXX", ylabel: str="YYY", title: str="Empty Title", typ: str="line"):
        """ Given x and y, plot a graph"""
        ax = self.__get_new_figure(title=title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        try:
            if typ == "line":
                ax.plot(xdata, ydata)
            elif typ == "scatter":
                ax.scatter(xdata, ydata)
            else:
                raise RuntimeError("Invalid plot type")
        except RuntimeError as error:
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
            
        ax.legend(fontsize=8)

    

    def plt_lambda_loss_csv(self):
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

                
                # Drop the unwanted lengths
                if self.configs["columns_drop"][name] is not None:
                    df_dropped = df_dropped.loc[:, [not x for x in df_dropped.columns.str.startswith(tuple(self.configs["columns_drop"][name]))]]
                
                df_dropped["Wavelength"] = df_dropped["Wavelength"]*1e+09
                #df_dropped.loc[:,"Wavelength"] = df_dropped.loc[:,'Wavelength']*1e+09 # make sure that wavelength is in nm

                for i in range(no_channels):
                    label = f'{name}_{sheet}' if no_channels == 1 else f'{name}_{sheet}_CH{i}'
                    
                    # obtain the columns from the correct channel
                    temp = df_dropped.loc[:, df_dropped.columns.str.endswith(f'CH{i}')]
                    temp.columns = [float(t.split(" - ")[0]) for t in temp.columns.values] # replaces the index with only the length
                    temp = temp.sort_index(axis=1, ascending=True) # sort out the index in ascending order
                    
                    # extract the lengths out of headers
                    xdata = temp.columns.values
                    # get a loss averaged over a specified wavelength range for each length
                    ydata = self.get_avgdata(df=df_dropped, avg_range=avg_range, target_lambda=exp_lambda) # get the average data

                    # linear regression
                    xline, yline, fit = self.linear_regression(xdata, ydata)

                    # plot data
                    ax.plot(xline, yline, ':')
                    ax.scatter(xdata, ydata, label=label)
                    offset = f'+{round(fit[1],4)}' if fit[1] > 0 else round(fit[1], 4) if fit[1] < 0 else 0
                    print(f'{name}_CH{i} : y = {round(fit[0],4)}x {offset}')
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
                if self.configs["columns_plot"][name] is not None:
                    df_dropped = df_dropped.loc[:, [x for x in df_dropped.columns.str.startswith(tuple(self.configs["columns_plot"][name]))]]

                xdata = df_dropped.loc[:,'Wavelength']*1e+09

                for i in range(no_channels):
                    # obtain the columns from the correct channel
                    temp = df_dropped.loc[:, df_dropped.columns.str.endswith(f'CH{i}')]
                    temp.columns = [float(t.split(" - ")[0]) for t in temp.columns.values] # replaces the index with only the length
                    temp = temp.sort_index(axis=1, ascending=True) # sort out the index in ascending order
                    
                    for length in temp.columns.values:
                        label = f'{name}_{length}{self.configs["end_of_legend"]}' if no_channels == 1 else f'{name}_CH{i}_{length}{self.configs["end_of_legend"]}'
                        ydata = np.negative(temp.loc[:,length])
                        ax.plot(xdata, ydata, label=label)
        ax.legend(fontsize=8)
