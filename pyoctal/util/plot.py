from pyoctal.util.file_operations import get_dataframe_from_csv, get_dataframe_from_excel

import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
from collections import deque
import matplotlib.animation as animation
import logging

logger = logging.getLogger(__name__)

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
        _, axes = self._get_new_figure()
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axes = axes
        self.lineplot, = axes.plot([], [], "-")
        self.axes.get_autoscaley_on()

    @staticmethod
    def _get_new_figure():
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

    def __init__(self, configs, **kwargs):
        self.configs = configs
        self.no_channels = configs.no_channels
        self.title = configs.title
        self.sf = configs.signal_filter
        self.xlabel = configs.xlabel
        self.ylabel = configs.ylabel
        self.files = kwargs["files"]
        self.columns_drop = kwargs["columns_drop"]
        self.columns_plot = kwargs["columns_plot"]
        self.markers = ["*", "^", "o", "+", "."]

    @staticmethod
    def _get_new_figure(title):
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
    def show():
        plt.show()


    @staticmethod
    def linear_regression(xdata, ydata):
        fit = np.polyfit(xdata, ydata, deg=1)

        xline = np.linspace(min(xdata), max(xdata))
        yline = xline*fit[0] + fit[1]

        return xline, yline, fit

    @staticmethod
    def normalise(ydata):
        """ Normalise all data to the lowest loss. """
        return ydata - ydata[0]

    @staticmethod
    def get_avgdata(wavelength, df: pd.DataFrame, avg_range: float, target_lambda) -> pd.DataFrame:
        """ Average the datapoints across a wavelength range for each length """

        if avg_range == 0: # only want a specific wavelength data
            return df.iloc[(wavelength - target_lambda).abs().argsort()[:1]].values[0][1:]
        
        upper_lambda = target_lambda + avg_range/2
        lower_lambda = target_lambda - avg_range/2
        upper_rindex = (wavelength - upper_lambda).abs().argsort()[:1].values[0]
        lower_rindex = (wavelength - lower_lambda).abs().argsort()[:1].values[0]

        # get the row mean and remove the wavelength data
        df_avg = np.negative(df.iloc[lower_rindex:upper_rindex, :].mean(axis=0).values)
        return df_avg
    

    @staticmethod
    def signal_filter(data: pd.Series, window_size: int):
        """ Moving average filtering technique """
        return data.rolling(window=window_size).mean()


    @staticmethod
    def calc_dc_params(df: pd.DataFrame):
        pass


    @classmethod
    def get_all_funcnames(cls):
        method_list = [method for method in dir(cls) if method.startswith('__') is False or method.startswith('_') is False]
        # filter out specific ones
        method_list = filter(lambda x: x.startswith("plt_"), method_list)
        return method_list


    def plt_data(self, xdata, ydata, xlabel: str="XXX", ylabel: str="YYY", title: str="Empty Title", typ: str="line"):
        """ Given x and y, plot a graph"""
        ax = self._get_new_figure(title=title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        if typ == "line":
            ax.plot(xdata, ydata)
        elif typ == "scatter":
            ax.scatter(xdata, ydata)
        else:
            raise RuntimeError("Invalid plot type")


    def plt_len_loss_excel(self):
        """ Plot a loss v.s. length graph with the data from a excel file """
        exp_lambda = self.configs.exp_lambda
        avg_range = self.configs.lambda_avgrange
        mk_idx = 0

        ax = self._get_new_figure(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        for filepath, sheetnames in self.files.items():

            df = get_dataframe_from_excel(filepath=filepath, sheet_names=sheetnames)
            
            for sheet in sheetnames:
                df_dropped = df[sheet]
                wavelength = df_dropped["Wavelength"]*1e+09
                df_dropped = df_dropped.drop("Wavelength", axis=1)

                # Drop the unwanted lengths
                folder_name = filepath.split('/')[-2]
                if self.columns_drop is not None and self.columns_drop.get(filepath) and self.columns_drop[filepath].get(sheet):
                    df_dropped = df_dropped.loc[:, [not x for x in df_dropped.columns.str.startswith(tuple(map(str, self.columns_drop[filepath][sheet])))]]
                
                df_dropped = df_dropped.apply(lambda x: self.signal_filter(x, window_size=self.configs.window_size)) if self.sf else df_dropped # filter out the noise
                
                # obtain the columns from the correct channel
                df_dropped.columns = [float(t.split(" - ")[0]) for t in df_dropped.columns.values] # replaces the index with only the length
                df_dropped = df_dropped.sort_index(axis=1, ascending=True) # sort out the index in ascending order

                # extract the lengths out of headers
                xdata = df_dropped.columns.values
                # get a loss averaged over a specified wavelength range for each length
                ydata = self.get_avgdata(wavelength=wavelength, df=df_dropped, avg_range=avg_range, target_lambda=exp_lambda) # get the average data

                if self.configs.normalise:
                    ydata = self.normalise(ydata)

                # linear regression
                xline, yline, fit = self.linear_regression(xdata, ydata)
                
                # plot data
                ax.scatter(xdata, ydata, label="data", marker=self.markers[mk_idx], color="red")
                mk_idx += 1
                ax.plot(xline, yline, ":", label="fit")
                offset = f'+{round(fit[1],4)}' if fit[1] > 0 else round(fit[1], 4) if fit[1] < 0 else 0
                logger.info(f'{folder_name} : y = {round(fit[0],4)}x {offset}')
        ax.legend(fontsize=8)


    def plt_lambda_loss_excel(self):
        """ Plot a loss v.s. wavelength graph with the data from a excel file """
        ax = self._get_new_figure(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        for filepath, sheetnames in self.files.items():
            
            df = get_dataframe_from_excel(folder=filepath, fname=self.fname, sheet_names=sheetnames)
            
            for sheet in self.configs.sheets:
                df_dropped = df[sheet]
                xdata = df_dropped.loc[:,'Wavelength']*1e+09

                # plot the wanted columns
                folder_name = filepath.split('/')[-2]
                if self.columns_plot is not None and self.columns_plot.get(filepath) and self.columns_plot[filepath].get(sheet):
                    df_dropped = df_dropped.loc[:, list(df_dropped.columns.str.startswith(tuple(map(str, self.columns_plot[folder_name][sheet]))))]


                # obtain the columns from the correct channel
                df_dropped.columns = [float(t.split(" - ")[0]) for t in df_dropped.columns.values] # replaces the index with only the length
                df_dropped = df_dropped.sort_index(axis=1, ascending=True) # sort out the index in ascending order
                
                for length in df_dropped.columns.values:
                    label = label + " " + self.configs.end_of_legend if not self.configs.end_of_legend == "" else label
                    ydata = np.negative(df_dropped.loc[:,length])
                    ydata = self.signal_filter(data=ydata, window_size=self.configs.window_size) if self.sf else ydata
                    ax.plot(xdata, ydata, label=label)
        ax.legend(fontsize=8)


