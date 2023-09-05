import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
from collections import deque
import matplotlib.animation as animation
import logging
from typing import Union, Tuple

from pyoctal.util.file_operations import get_dataframe_from_csv, get_dataframe_from_excel

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
        self.save = configs.save
        self.save_fpath = configs.save_fpath

    @staticmethod
    def _save_img(fig, fname: str, dpi: float=300):
        fig.savefig(fname=fname, dpi=dpi)

    @staticmethod
    def _get_new_figure(title):
        """ Obtain a new figure """
        fig = plt.figure()
        ax = fig.add_axes([0.15,0.15,0.75,0.75])
        ax.set_title(title)
        ax.minorticks_on()
        #ax.grid(True)
        #ax.grid(which='major', color='#DDDDDD', linewidth=0.8)
        #ax.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
        
        return fig, ax
    
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
    def get_avgdata(x: pd.Series, df: pd.DataFrame, avg_range: float, target_x: float) -> pd.DataFrame:
        """ Average the datapoints across a wavelength range for each length """
        if avg_range == 0: # only want a specific wavelength data
            return np.negative(df.iloc[(x - target_x).abs().argsort()[:1]].values[0])
        
        upper_x = target_x + avg_range/2
        lower_x = target_x - avg_range/2
        upper_ridx = (x - upper_x).abs().argsort()[:1].values[0]
        lower_ridx = (x - lower_x).abs().argsort()[:1].values[0]

        # get the row mean and remove the wavelength data
        df_avg = np.negative(df.iloc[lower_ridx:upper_ridx, :].mean(axis=0).values)
        return df_avg
    

    @staticmethod
    def signal_filter(data: pd.Series, window_size: int):
        """ Moving average filtering technique """
        return data.rolling(window=window_size).mean()


    @staticmethod
    def calc_dc_params(df: pd.DataFrame):
        pass

    @staticmethod
    def x_plt_range(xdata: pd.Series, x_range: Union[tuple, list]) -> Tuple[list, list]:
        # wavelength[0] = start wavelength, wavelength[1] = stop wavelength
        start_idx = (xdata - x_range[0]).abs().argsort()[:1].values[0]
        stop_idx = (xdata - x_range[1]).abs().argsort()[:1].values[0]
        return start_idx, stop_idx


    @classmethod
    def get_all_funcnames(cls):
        method_list = [method for method in dir(cls) if method.startswith('__') is False or method.startswith('_') is False]
        # filter out specific ones
        method_list = filter(lambda x: x.startswith("plt_"), method_list)
        return method_list
    


    def plt_data(self, xdata, ydata, xlabel: str="XXX", ylabel: str="YYY", title: str="Empty Title", typ: str="line"):
        """ Given x and y, plot a graph"""
        fig, ax = self._get_new_figure(title=title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        if typ == "line":
            ax.plot(xdata, ydata)
        elif typ == "scatter":
            ax.scatter(xdata, ydata)
        else:
            raise RuntimeError("Invalid plot type")

    def plt_len_loss_csv(self):
        """ Plot a loss v.s. length graph with the data from a csv file """
        exp_lambda = self.configs.exp_lambda
        avg_range = self.configs.lambda_avgrange

        fig, ax = self._get_new_figure(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        for idx, (filepath, _) in enumerate(self.files.items()):

            df = get_dataframe_from_csv(filepath=filepath)
            
            wavelength = df["Wavelength"]*1e+09
            df = df.drop("Wavelength", axis=1)

            # Drop the unwanted lengths
            if self.columns_drop is not None and self.columns_drop.get(filepath):
                wanted_column_names = [not x.startswith(tuple(map(str, self.columns_drop[filepath]))) for x in map(str, df.columns)]
                df = df.loc[:, wanted_column_names]
            
            df = df.apply(lambda x: self.signal_filter(x, window_size=self.configs.window_size)) if self.sf else df # filter out the noise
            
            # obtain the columns from the correct channel
            df.columns = df.columns.astype(float)
            df = df.sort_index(axis=1, ascending=True) # sort out the index in ascending order

            # extract the lengths out of headers
            xdata = df.columns.values
            # get a loss averaged over a specified wavelength range for each length
            ydata = self.get_avgdata(x=wavelength, df=df, avg_range=avg_range, target_x=exp_lambda) # get the average data
            if self.configs.normalise:
                ydata = self.normalise(ydata)

            # linear regression
            xline, yline, fit = self.linear_regression(xdata, ydata)
            
            # plot data
            ax.scatter(xdata, ydata, label="data", marker=self.markers[idx])
            ax.plot(xline, yline, ":", label="fit")
            offset = f'+{round(fit[1],4)}' if fit[1] > 0 else round(fit[1], 4) if fit[1] < 0 else 0
            logger.info(f'{filepath} : y = {round(fit[0],4)}x {offset}')
        ax.legend(fontsize=8)

        if self.save:
            self._save_img(fig=fig, fname=self.save_fpath)

    def plt_lambda_loss_csv(self):
        """ Plot a loss v.s. wavelength graph with the data from a csv file """
        fig, ax = self._get_new_figure(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        for filepath, _ in self.files.items():
            
            df = get_dataframe_from_csv(filepath=filepath)
            
            xdata = df.loc[:,'Wavelength']*1e+09
            df = df.drop(['Wavelength'], axis=1)

            # check if there is a plot range
            if self.configs.x_range and self.configs.x_range.get("start") and self.configs.x_range.get("stop"):
                idx_start, idx_stop = self.x_plt_range(xdata=xdata, x_range=(self.configs.x_range.start, self.configs.x_range.stop))
                xdata = xdata[idx_start:idx_stop]

            # plot the wanted columns
            if self.columns_plot is not None and self.columns_plot.get(filepath):
                wanted_column_names = [x.startswith(tuple(map(str, self.columns_plot[filepath]))) for x in map(str, df.columns)]
                df = df.loc[:, wanted_column_names]


            # sort out the column index
            df.columns = df.columns.astype(float)
            df = df.sort_index(axis=1, ascending=True).reset_index(drop=True) # sort out the index in ascending order
            
            for length in df.columns.values:
                label = str(length) + self.configs.end_of_legend
                ydata = df.loc[:,length]
                ydata = self.signal_filter(data=ydata, window_size=self.configs.window_size) if self.sf else ydata
                if self.configs.x_range and self.configs.x_range.get("start") and self.configs.x_range.get("stop"):
                    ydata = ydata[idx_start:idx_stop]
                ax.plot(xdata, ydata, label=label)
        ax.legend(fontsize=8)
        if self.save:
            self._save_img(fig=fig, fname=self.save_fpath)



    def plt_len_loss_excel(self):
        """ Plot a loss v.s. length graph with the data from a excel file """
        exp_lambda = self.configs.exp_lambda
        avg_range = self.configs.lambda_avgrange

        fig, ax = self._get_new_figure(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        for i, (filepath, sheetnames) in enumerate(self.files.items()):

            df = get_dataframe_from_excel(filepath=filepath, sheet_names=sheetnames)
            
            for j, sheet in enumerate(sheetnames):
                df_dropped = df[sheet]
                wavelength = df_dropped["Wavelength"]*1e+09
                df_dropped = df_dropped.drop("Wavelength", axis=1)

                # Drop the unwanted lengths
                if self.columns_drop is not None and self.columns_drop.get(filepath) and self.columns_drop[filepath].get(sheet):
                    wanted_column_names = [not x.startswith(tuple(map(str, self.columns_drop[filepath][sheet]))) for x in map(str, df_dropped.columns)]
                    df_dropped = df_dropped.loc[:, wanted_column_names]
                
                df_dropped = df_dropped.apply(lambda x: self.signal_filter(x, window_size=self.configs.window_size)) if self.sf else df_dropped # filter out the noise
                
                # obtain the columns from the correct channel
                df_dropped.columns = df_dropped.columns.astype(float)
                df_dropped = df_dropped.sort_index(axis=1, ascending=True) # sort out the index in ascending order

                # extract the lengths out of headers
                xdata = df_dropped.columns.values
                # get a loss averaged over a specified wavelength range for each length
                ydata = self.get_avgdata(x=wavelength, df=df_dropped, avg_range=avg_range, target_x=exp_lambda) # get the average data

                if self.configs.normalise:
                    ydata = self.normalise(ydata)

                # linear regression
                xline, yline, fit = self.linear_regression(xdata, ydata)
                
                # plot data
                ax.scatter(xdata, ydata, label="data", marker=self.markers[i*len(sheetnames)+j])
                ax.plot(xline, yline, ":", label="fit")
                offset = f'+{round(fit[1],4)}' if fit[1] > 0 else round(fit[1], 4) if fit[1] < 0 else 0
                logger.info(f'{filepath} : y = {round(fit[0],4)}x {offset}')
        ax.legend(fontsize=8)

        if self.save:
            self._save_img(fig=fig, fname=self.save_fpath)


    def plt_lambda_loss_excel(self):
        """ Plot a loss v.s. wavelength graph with the data from a excel file """
        fig, ax = self._get_new_figure(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        for filepath, sheetnames in self.files.items():
            
            df = get_dataframe_from_excel(filepath=filepath, sheet_names=sheetnames)
            
            for sheet in sheetnames:
                df_dropped = df[sheet]
                
                xdata = df_dropped.loc[:,'Wavelength']*1e+09
                df_dropped = df_dropped.drop(['Wavelength'], axis=1)
                
                # check if there is a plot range
                if self.configs.x_range and self.configs.x_range.get("start") and self.configs.x_range.get("stop"):
                    idx_start, idx_stop = self.x_plt_range(xdata=xdata, x_range=(self.configs.x_range.start, self.configs.x_range.stop))
                    xdata = xdata[idx_start:idx_stop]

                # plot the wanted columns
                if self.columns_plot and self.columns_plot.get(filepath) and self.columns_plot[filepath].get(sheet):
                    wanted_column_names = [x.startswith(tuple(map(str, self.columns_plot[filepath][sheet]))) for x in map(str, df_dropped.columns)]
                    df_dropped = df_dropped.loc[:, wanted_column_names]


                # obtain the columns from the correct channel
                df_dropped.columns = df_dropped.columns.astype(float)
                df_dropped = df_dropped.sort_index(axis=1, ascending=True) # sort out the index in ascending order
                
                for length in df_dropped.columns.values:
                    label = str(length) + self.configs.end_of_legend
                    ydata = np.negative(df_dropped.loc[:,length])
                    ydata = self.signal_filter(data=ydata, window_size=self.configs.window_size) if self.sf else ydata
                    if self.configs.x_range and self.configs.x_range.get("start") and self.configs.x_range.get("stop"):
                        ydata = ydata[idx_start:idx_stop]
                    ax.plot(xdata, ydata, label=label)
        ax.legend(fontsize=8)
        if self.save:
            self._save_img(fig=fig, fname=self.save_fpath)


