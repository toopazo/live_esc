#!/usr/bin/python3

import sys
import os
import matplotlib
import pandas
import argparse
import datetime
import matplotlib.pyplot as plt
from toopazo_tools.file_folder import FileFolderTools as FFTools

# Check if this is running inside toopazo_ulg/ or deployed as a module
if os.path.isfile('kdecan_parse.py'):
    from kdecan_parse import KdecanParser
else:
    from live_esc.kde_uas85uvc.kdecan_parse import KdecanParser


class KdecanPlot:
    """
    Class to plot data from log
    """

    def __init__(self, bdir, time_win):
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

        self.time_win = time_win

        matplotlib.use('Qt5Agg')

    def save_current_plot(self, kdecan_file, tag_arr, sep, ext):
        assert isinstance(kdecan_file, str)
        (head, tail) = os.path.split(kdecan_file)
        kdecan_file = tail
        name = kdecan_file.replace(self.file_extension, "")
        for tag in tag_arr:
            name = name + sep + str(tag)
        file_path = self.plotdir + '/' + name + ext

        # plt.show()
        plt.savefig(file_path)
        # return file_path

    def process_file(self, kdecan_file):
        print('[process_file] Working on file %s' % kdecan_file)
        kdecan_df = KdecanParser.get_pandas_dataframe(kdecan_file, self.time_win)
        print(kdecan_df)

        for escid in range(11, 19):
            df_tmp = kdecan_df[kdecan_df[KdecanParser.col_escid] == escid]
            col_arr = [KdecanParser.col_voltage, KdecanParser.col_current, KdecanParser.col_rpm,
                       KdecanParser.col_inthtl, KdecanParser.col_outthtl]
            df_tmp = df_tmp[col_arr]
            # df_tmp['power'] = df_tmp[self.col_voltage] * df_tmp[self.col_current]
            df_tmp.plot(figsize=self.figsize, subplots=True)
            self.save_current_plot(kdecan_file, tag_arr=["escid{}".format(escid)], sep="_", ext='.png')

    def process_folder(self):
        print('[process_folder] Working on folder %s' % self.logdir)
        # foldername, extension, method
        FFTools.run_method_on_folder(self.logdir, self.file_extension, self.process_file)

    def find_kdecan_file(self, log_num):
        kdecan_file = 'No such file'
        file_arr = FFTools.get_file_arr(fpath=self.logdir, extension=self.file_extension)
        for file in file_arr:
            if log_num is not None:
                pattern = f'_{log_num}_'
                if pattern in file:
                    kdecan_file = os.path.abspath(file)
                    break
        print(f'[find_kdecan_file] logdir {self.logdir}')
        print(f'[find_kdecan_file] file_extension {self.file_extension}')
        print(f'[find_kdecan_file] log_num {log_num}')
        print(f'[find_kdecan_file] kdecan_file {kdecan_file}')
        return kdecan_file


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

    kdecan_plot = KdecanPlot(os.path.abspath(args.bdir), args.time_win)
    if args.log_num is not None:
        kdecan_plot.process_file(kdecan_file=kdecan_plot.find_kdecan_file(args.log_num))
    else:
        kdecan_plot.process_folder()

    # ufilename = sys.argv[1]
    # ufilename = parse_user_arg(ufilename)
    # uindexcol = sys.argv[2]

    # Header of kdecan log file log_1_2021-09-16-19-05-59.kdecan
    #     time s, escid, voltage V, current A, angVel rpm, temp degC,
    #     warning, inthtl us, outthtl perc

    #
    # plotlog = KdecanPlot(ufilename, uindexcol)
    # udataframe = plotlog.dataframe
    # print(udataframe)
    # for escid in range(11, 19):
    #     df_tmp = udataframe[udataframe[col_escid] == escid]
    #     col_arr = [col_voltage, col_current, col_rpm, col_inthtl, col_outthtl]
    #     plotlog.plot_dataframe(df_tmp[col_arr])
    #     plotlog.save_current_plot(
    #         tag_arr=["escid{}".format(escid)], sep="_", ext='.png')
