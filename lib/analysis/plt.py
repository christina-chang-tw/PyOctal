from lib.util.file_operations import get_result_dirpath, get_dataframe_from_csv, get_dataframe_from_excel
from lib.analysis.iloss import iloss_coeffs
from lib.util.file_operations import export_to_csv, export_to_excel

import matplotlib.pyplot as plt 
import numpy as np



class PlotGraphs(object):

    coeffs_name = "iloss_coeffs"
    data_name = "iloss_data"
    info_name = "iloss_info"

    def __init__(self, exp_wavelength: float=1550):
        self.exp_wavelength = exp_wavelength

    @staticmethod
    def __get_new_figure():
        fig = plt.figure()
        ax = fig.add_axes([0.1,0.1,0.8,0.8])
        ax.minorticks_on()
        return ax


    def plt_len_loss_csv(self, chips: tuple, columns_dropping, structure: str="XXX", unit: str="um"):

        ax = self.__get_new_figure()
        ax.set_xlabel(f'Length [{unit}]')
        ax.set_ylabel(f'Loss [dB/{unit}]')
        ax.set_title('Insertion Loss of Different Chips')

        for name in chips:
            df_coeff = []

            df = get_dataframe_from_csv(dir=get_result_dirpath(name), fname=f"{structure}_{self.data_name}")
            info = get_dataframe_from_csv(dir=get_result_dirpath(name), fname=f"{structure}_{self.info_name}")

            no_channels = int(info.loc[info["Params"] == "Number of channels"].loc[:,"Value"])
            df_dropped = df.loc[:, [not x for x in df.columns.str.endswith(tuple(columns_dropping[name]))]]

            for i in range(no_channels):
                label = f'{name}' if no_channels == 1 else f'{name}_CH{i}'
                temp = df_dropped.loc[:, df_dropped.columns.str.startswith(f'CH{i}')]

                xdata = [float(i.split(" - ")[1]) for i in temp.columns.values[0:]]
                ydata = temp.iloc[(df_dropped['Wavelength'] - self.exp_wavelength).abs().argsort()[:1]].values[0][0:]

                # linear regression
                fit = np.polyfit(xdata, ydata, deg=1)
                xline = np.linspace(min(xdata), max(xdata))
                yline = xline*fit[0] + fit[1]

                ax.plot(xline, yline, ':')
                ax.scatter(xdata, ydata, label=label)
                print(f'{name}_CH{i} : y = {round(fit[0],4)}x {round(fit[1],4)}')
                df_coeff = iloss_coeffs(df=temp, wavelengths=df_dropped['Wavelength'], lengths=xdata, no_channels=no_channels, unit=unit)
            
            export_to_csv(df_coeff, get_result_dirpath(name), f'{structure}_iloss_coeffs')
        ax.legend(fontsize=8)
    

    def plt_lambda_loss(self, chips: tuple, columns_plot, structure: str="XXX", unit: str="mm"):
        
        ax = self.__get_new_figure()
        ax.set_xlabel(f'Wavelength [nm]')
        ax.set_ylabel(f'Loss [dB/{unit}]')
        ax.set_title('Insertion Loss of Different Wavelengths')

        for name in chips:

            df = get_dataframe_from_csv(dir=get_result_dirpath(name), fname=f"{structure}_{self.data_name}")
            info = get_dataframe_from_csv(dir=get_result_dirpath(name), fname=f"{structure}_{self.info_name}")

            no_channels = int(info.loc[info["Params"] == "Number of channels"].loc[:,"Value"])
            df_dropped = df.loc[:, [x for x in df.columns.str.endswith(tuple(columns_plot[name]))]]

            xdata = df['Wavelength']

            for i in range(no_channels):
                temp = df_dropped.loc[:, df_dropped.columns.str.startswith(f'CH{i}')]
                
                for length in temp.columns.values:
                    label = f'{name}_{length.split(" - ")[1]}{unit}' if no_channels == 1 else f'{name}_{length}{unit}'
                    ydata = temp.loc[:,length]
                    ax.plot(xdata, ydata, label=label)
        ax.legend(fontsize=8)


    def plt_coeffs(self, chips: tuple, structure: str="XXX", unit: str="mm"):
        
        ax1 = self.__get_new_figure()
        ax1.set_xlabel(f'Wavelength [nm]')
        ax1.set_ylabel(f'Loss [dB/{unit}]')
        ax1.set_title('Waveguide Loss of Different Wavelengths')

        ax2 = self.__get_new_figure()
        ax2.set_xlabel(f'Wavelength [nm]')
        ax2.set_ylabel(f'Insertion Loss [dB]')
        ax2.set_title('Insertion Loss of Different Wavelengths')

        for name in chips:

            df_coeffs = get_dataframe_from_csv(dir=get_result_dirpath(name), fname=f"{structure}_{self.coeffs_name}")
            info = get_dataframe_from_csv(dir=get_result_dirpath(name), fname=f"{structure}_{self.info_name}")
            
            no_channels = int(info.loc[info["Params"] == "Number of channels"].loc[:,"Value"])
            xdata = df_coeffs['Wavelength']

            for i in range(no_channels):
                label = f'{name}' if no_channels == 1 else f'{name}_CH{i}'
                ax1.plot(xdata, df_coeffs[f"CH{i} - loss [db/{unit}]"], label=label)
                ax2.plot(xdata, df_coeffs[f"CH{i} - insertion loss [dB]"], label=label)

        ax1.legend(fontsize=8)
        ax2.legend(fontsize=8)


    def plt_len_loss_excel(self, chips: tuple, columns_dropping, sheet_names, structure: str="XXX", unit: str="um"):

        ax = self.__get_new_figure()
        ax.set_xlabel(f'Length [{unit}]')
        ax.set_ylabel(f'Loss [dB/{unit}]')
        ax.set_title('Insertion Loss of Different Chips')

        for name in chips:

            df, info = get_dataframe_from_excel(dir=get_result_dirpath(name), fname=f"{structure}_{self.data_name}", sheet_names=sheet_names)
            for sheet in sheet_names:
                df_coeff = []

                no_channels = int(info.loc[info["General:"] == "NumberOfChannels"].loc[:, "Unnamed: 1"])
                df_dropped = df[sheet].loc[:, [not x for x in df[sheet].columns.str.endswith(tuple(columns_dropping[name]))]]
                wavelength = df_dropped['Wavelength']*1e+09

                for i in range(no_channels):
                    label = f'{name}_{sheet}' if no_channels == 1 else f'{name}_{sheet}_CH{i}'
                    temp = df_dropped.loc[:, df_dropped.columns.str.startswith(f'CH{i}')]
           
                    xdata = [float(i.split(" - ")[1]) for i in temp.columns.values[0:]]
                    ydata = temp.iloc[(wavelength - self.exp_wavelength).abs().argsort()[:1]].values[0][0:]

                    # linear regression
                    fit = np.polyfit(xdata, ydata, deg=1)
                    xline = np.linspace(min(xdata), max(xdata))
                    yline = xline*fit[0] + fit[1]

                    ax.plot(xline, yline, ':')
                    ax.scatter(xdata, ydata, label=label)
                    offset = f'+{round(fit[1],4)}' if fit[1] > 0 else round(fit[1], 4) if fit[1] < 0 else 0
                    print(f'{name}_CH{i} : y = {round(fit[0],4)}x {offset}')
                    df_coeff = iloss_coeffs(df=temp, wavelengths=wavelength, lengths=xdata, no_channels=no_channels, unit=unit)
                
                export_to_excel(df_coeff, get_result_dirpath(name), f'{structure}_iloss_coeffs')
        ax.legend(fontsize=8)


    def plt_lambda_loss_excel(self, chips: tuple, columns_plot, sheet_names, structure: str="XXX", unit: str="mm"):
        
        ax = self.__get_new_figure()
        ax.set_xlabel(f'Wavelength [nm]')
        ax.set_ylabel(f'Loss [dB/{unit}]')
        ax.set_title('Insertion Loss of Different Wavelengths')

        for name in chips:
            
            df, info = get_dataframe_from_excel(dir=get_result_dirpath(name), fname=f"{structure}_{self.data_name}", sheet_names=sheet_names)
            
            for sheet in sheet_names:
                
                no_channels = int(info.loc[info["General:"] == "NumberOfChannels"].loc[:, "Unnamed: 1"])
                df_dropped = df[sheet].loc[:, [x for x in df[sheet].columns.str.endswith(tuple(columns_plot[name]))]]
                
                xdata = df[sheet]['Wavelength']*1e+09

                for i in range(no_channels):
                    temp = df_dropped.loc[:, df_dropped.columns.str.startswith(f'CH{i}')]
                    
                    for length in temp.columns.values:
                        label = f'{name}_{length.split(" - ")[1]}{unit}' if no_channels == 1 else f'{name}_{length}{unit}'
                        ydata = np.negative(temp.loc[:,length])
                        ax.plot(xdata, ydata, label=label)
        ax.legend(fontsize=8)