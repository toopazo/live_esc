#!/usr/bin/python3

import sys
import matplotlib
import pandas
import matplotlib.pyplot as plt
from toopazo_tools.file_folder import FileFolderTools as FFTools


class PlotTelemetryLog:
    """
    Class to plot data from log
    """

    def __init__(self, filepath, index_col):
        self.file_path = filepath
        [head, tail] = FFTools.get_file_split(filepath)
        self.file_folder = head
        self.file_name = tail
        [root, ext] = FFTools.get_file_splitext(filepath)
        _ = root
        self.file_extension = ext

        self.dataframe = pandas.read_csv(
            self.file_path, index_col=index_col, parse_dates=True)
        # self.dataframe.set_index(
        #     index_col, inplace=True, verify_integrity=True)
        # print(self.dataframe)
        # print(self.dataframe.shape)
        # print(self.dataframe.columns)
        # print(self.dataframe.iterrows())

        matplotlib.use('Qt5Agg')

    def save_current_plot(self, tag_arr, sep, ext):
        assert isinstance(self.file_name, str)
        name = self.file_name.replace(self.file_extension, "")
        for tag in tag_arr:
            name = name + sep + str(tag)
        file_path = self.file_folder + '/' + name + ext

        # plt.show()
        plt.savefig(file_path)
        # return file_path

    def plot_dataframe(self, dataframe):
        tfigsize = (12, 6)
        # fig, axs = plt.subplots(figsize=tfigsize)
        # df.plot()
        # df.plot.area(ax=axs, subplots=True)
        dataframe.plot(figsize=tfigsize, subplots=True)

        # cmap = ListedColormap(['#0343df', '#e50000', '#ffff14', '#929591'])
        # ax = df.plot.bar(x='year', colormap=cmap)
        # ax.set_xlabel(None)
        # ax.set_ylabel('Seats')
        # ax.set_title('UK election results')


def parse_user_arg(filename):
    filename = FFTools.full_path(filename)
    print('target file {}'.format(filename))
    if FFTools.is_file(filename):
        cwd = FFTools.get_cwd()
        print('current folder {}'.format(cwd))
    else:
        arg = '{} is not a file'.format(filename)
        raise RuntimeError(arg)
    return filename


if __name__ == '__main__':
    ufilename = sys.argv[1]
    ufilename = parse_user_arg(ufilename)
    uindexcol = sys.argv[2]

    # Header of kdecan log file log_1_2021-09-16-19-05-59.kdecan
    #     time s, escid, voltage V, current A, angVel rpm, temp degC,
    #     warning, inthtl us, outthtl perc

    col_escid = ' escid'
    col_voltage = ' voltage V'
    col_current = ' current A'
    col_rpm = ' angVel rpm'
    col_temp = ' temp degC'
    col_warn = ' warning'
    col_inthtl = ' inthtl us'
    col_outthtl = ' outthtl perc'

    plotlog = PlotTelemetryLog(ufilename, uindexcol)
    for escid in range(11, 19):
        udataframe = plotlog.dataframe
        udataframe = udataframe[udataframe[col_escid] == escid]
        col_arr = [col_voltage, col_current, col_rpm, col_inthtl, col_outthtl]
        plotlog.plot_dataframe(udataframe[col_arr])
        plotlog.save_current_plot(
            tag_arr=["escid{}".format(escid)], sep="_", ext='.png')
