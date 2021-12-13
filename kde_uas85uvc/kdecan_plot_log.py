#!/usr/bin/python3

import sys
import os
import matplotlib
import pandas
import argparse
import datetime
import matplotlib.pyplot as plt
from toopazo_tools.file_folder import FileFolderTools as FFTools


class PlotKdecanLog:
    """
    Class to plot data from log
    """

    def __init__(self, bdir, log_num, time_win):
        # bdir = FFTools.full_path(args.bdir)
        # bdir = os.path.abspath(args.bdir)
        self.logdir = bdir + '/logs'
        self.tmpdir = bdir + '/tmp'
        self.plotdir = bdir + '/plots'
        try:
            if not os.path.isdir(self.logdir):
                os.mkdir(self.logdir)
            if not os.path.isdir(self.tmpdir):
                os.mkdir(self.logdir)
            if not os.path.isdir(self.plotdir):
                os.mkdir(self.logdir)
        except OSError:
            raise RuntimeError('Directories are not present and could not be created')

        # self.file_path = filepath
        # [head, tail] = FFTools.get_file_split(filepath)
        # self.file_folder = head
        # self.file_name = tail
        # [root, ext] = FFTools.get_file_splitext(filepath)
        # _ = root
        self.file_extension = 'kdecan'
        self.figsize = (12, 6)

        self.col_time = 'time s'
        self.col_escid = 'escid'
        self.col_voltage = 'voltage V'
        self.col_current = 'current A'
        self.col_rpm = 'angVel rpm'
        self.col_temp = 'temp degC'
        self.col_warn = 'warning'
        self.col_inthtl = 'inthtl us'
        self.col_outthtl = 'outthtl perc'

        self.log_num = log_num
        self.time_win = time_win

        matplotlib.use('Qt5Agg')

    def save_current_plot(self, kdecanfile, tag_arr, sep, ext):
        assert isinstance(kdecanfile, str)
        (head, tail) = os.path.split(kdecanfile)
        kdecanfile = tail
        name = kdecanfile.replace(self.file_extension, "")
        for tag in tag_arr:
            name = name + sep + str(tag)
        file_path = self.plotdir + '/' + name + ext

        # plt.show()
        plt.savefig(file_path)
        # return file_path

    def process_file(self, kdecanfile):
        if self.log_num is not None:
            pattern = f'_{self.log_num}_'
            if pattern not in kdecanfile:
                return

        print('[process_file] Working on file %s' % kdecanfile)

        dataframe = pandas.read_csv(
            kdecanfile, index_col=self.col_time,
            parse_dates=True, skipinitialspace=True)
        dataframe = self.apply_time_win(dataframe)

        print(dataframe)
        for escid in range(11, 19):
            df_tmp = dataframe[dataframe[self.col_escid] == escid]
            col_arr = [self.col_voltage, self.col_current, self.col_rpm, self.col_inthtl, self.col_outthtl]
            df_tmp = df_tmp[col_arr]
            df_tmp.plot(figsize=self.figsize, subplots=True)
            self.save_current_plot(kdecanfile, tag_arr=["escid{}".format(escid)], sep="_", ext='.png')

    def process_logdir(self):
        print('[process_logdir] processing %s' % self.logdir)
        # foldername, extension, method
        FFTools.run_method_on_folder(self.logdir, self.file_extension, self.process_file)

    def apply_time_win(self, dataframe):
        if (self.time_win is not None) and (len(self.time_win) == 2):
            time_win_0 = datetime.datetime.strptime(self.time_win[0])
            time_win_1 = datetime.datetime.strptime(self.time_win[0])
            # df = df.loc[time_win[0] < df.index < time_win[1]]
            dataframe = dataframe.loc[time_win_0 < dataframe.index]
            dataframe = dataframe.loc[dataframe.index < time_win_1]
        return dataframe

# def parse_user_arg(filename):
#     filename = FFTools.full_path(filename)
#     print('target file {}'.format(filename))
#     if FFTools.is_file(filename):
#         cwd = FFTools.get_cwd()
#         print('current folder {}'.format(cwd))
#     else:
#         arg = '{} is not a file'.format(filename)
#         raise RuntimeError(arg)
#     return filename


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse, process and plot .kdecan files')
    parser.add_argument('--bdir', action='store', required=True,
                        help='Base directory of [logs, tmp, plots] folders')
    parser.add_argument('--log_num', action='store', default=None,
                        help='Specific log number to process')
    parser.add_argument('--time_win', action='store', default=None,
                        help='Specific time window to process', nargs=2, type=float)
    # parser.add_argument('--plot', action='store_true', required=False,
    #                     help='plot results')
    # parser.add_argument('--pos_vel', action='store_true', help='pos and vel')
    # parser.add_argument('--rpy_angles', action='store_true', help='roll, pitch and yaw attitude angles')
    # parser.add_argument('--pqr_angvel', action='store_true', help='P, Q, and R body angular velocity')
    # parser.add_argument('--man_ctrl', action='store_true', help='manual control')
    # parser.add_argument('--ctrl_alloc', action='store_true', help='Control allocation and in/out analysis')

    args = parser.parse_args()

    kdecan_data = PlotKdecanLog(os.path.abspath(args.bdir), args.log_num, args.time_win)
    kdecan_data.process_logdir()

    # ufilename = sys.argv[1]
    # ufilename = parse_user_arg(ufilename)
    # uindexcol = sys.argv[2]

    # Header of kdecan log file log_1_2021-09-16-19-05-59.kdecan
    #     time s, escid, voltage V, current A, angVel rpm, temp degC,
    #     warning, inthtl us, outthtl perc

    #
    # plotlog = PlotKdecanLog(ufilename, uindexcol)
    # udataframe = plotlog.dataframe
    # print(udataframe)
    # for escid in range(11, 19):
    #     df_tmp = udataframe[udataframe[col_escid] == escid]
    #     col_arr = [col_voltage, col_current, col_rpm, col_inthtl, col_outthtl]
    #     plotlog.plot_dataframe(df_tmp[col_arr])
    #     plotlog.save_current_plot(
    #         tag_arr=["escid{}".format(escid)], sep="_", ext='.png')
