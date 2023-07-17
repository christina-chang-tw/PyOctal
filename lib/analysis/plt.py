from lib.util.csv_operations import get_ddir_path, get_dataframe

import matplotlib.pyplot as plt 
import numpy as np

EXPECTED_WAVELENGTH = 1550


class PlotGraphs:

    @staticmethod
    def plt_len_loss(chips: tuple, columns_dropping, unit: str="um"):
        DATA_FNAME = "iloss_data_1.csv"
        INFO_FNAME = "iloss_info.csv"

        fig = plt.figure()
        ax = fig.add_axes([0.1,0.1,0.8,0.8])
        ax.set_xlabel(f'Length [{unit}]')
        ax.set_ylabel(f'Loss [dB/{unit}]')
        ax.set_title('Insertion Loss of Different Chips')

        for name in chips:
            data_path = f'{get_ddir_path()}/{name}/{DATA_FNAME}'
            info_path = f'{get_ddir_path()}/{name}/{INFO_FNAME}'

            df = get_dataframe(data_path)
            info = get_dataframe(info_path)

            no_channels = int(info.loc[info["Params"] == "Number of channels"].loc[:,"Value"])
            df_dropped = df.loc[:, [not x for x in df.columns.str.endswith(columns_dropping[name])]]

            for i in range(no_channels):
                label = f'{name}' if no_channels == 1 else f'{name}_CH{i}'
                temp = df_dropped.loc[:, df_dropped.columns.str.startswith(f'CH{i}')]

                xdata = [float(i.split(" - ")[1]) for i in temp.columns.values[0:]]
                ydata = temp.iloc[(df['lambda'] - EXPECTED_WAVELENGTH).abs().argsort()[:1]].values[0][0:]

                # linear regression
                fit = np.polyfit(xdata, ydata, deg=1)
                xline = np.linspace(min(xdata), max(xdata))
                yline = xline*fit[0] + fit[1]

                ax.plot(xline, yline, ':')
                ax.scatter(xdata, ydata, label=label)
                print(f'{name}_CH{i} : y = {round(fit[0],4)}x {round(fit[1],4)}')
               
        ax.legend()
        ax.minorticks_on()
            
    
    def plt_lambda_loss(self, chips: tuple, columns_plot, unit: str="mm"):
        DATA_FNAME = "iloss_data_1.csv"
        INFO_FNAME = "iloss_info.csv"
        
        fig = plt.figure()
        ax = fig.add_axes([0.1,0.1,0.8,0.8])
        ax.set_xlabel(f'Wavelength [nm]')
        ax.set_ylabel(f'Loss [dB/{unit}]')
        ax.set_title('Insertion Loss of Different Wavelengths')

        for name in chips:
            data_path = f'{get_ddir_path()}/{name}/{DATA_FNAME}'
            info_path = f'{get_ddir_path()}/{name}/{INFO_FNAME}'

            df = get_dataframe(data_path)
            info = get_dataframe(info_path)

            no_channels = int(info.loc[info["Params"] == "Number of channels"].loc[:,"Value"])
            df_dropped = df.loc[:, [x for x in df.columns.str.endswith(columns_plot[name])]]

            xdata = df['lambda']

            for i in range(no_channels):
                temp = df_dropped.loc[:, df_dropped.columns.str.startswith(f'CH{i}')]
                
                for length in temp.columns.values:
                    label = f'{name}_{length.split(" - ")[1]}{unit}' if no_channels == 1 else f'{name}_{length}{unit}'
                    ydata = temp.loc[:,length]
                    ax.plot(xdata, ydata, label=label)
        
        ax.legend()
        ax.minorticks_on()

