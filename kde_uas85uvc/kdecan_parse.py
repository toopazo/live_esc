#!/usr/bin/python3

import os
import pandas
import datetime


class KdecanParser:
    """
    Class to plot data from log
    """

    file_extension = 'kdecan'
    col_time = 'time s'
    col_escid = 'escid'
    col_voltage = 'voltage V'
    col_current = 'current A'
    col_rpm = 'angVel rpm'
    col_temp = 'temp degC'
    col_warn = 'warning'
    col_inthtl = 'inthtl us'
    col_outthtl = 'outthtl perc'

    # def __init__(self, kdecan_file, time_win):
    #     # bdir = FFTools.full_path(args.bdir)
    #     # bdir = os.path.abspath(args.bdir)
    #     self.kdecan_file = kdecan_file
    #     if not os.path.isfile(self.kdecan_file):
    #         raise RuntimeError(f'[KdecanParser] No such file {self.kdecan_file}')
    #
    #     # self.file_path = filepath
    #     # [head, tail] = FFTools.get_file_split(filepath)
    #     # self.file_folder = head
    #     # self.file_name = tail
    #     # [root, ext] = FFTools.get_file_splitext(filepath)
    #     # _ = root
    #     self.file_extension = 'kdecan'
    #
    #     self.col_time = 'time s'
    #     self.col_escid = 'escid'
    #     self.col_voltage = 'voltage V'
    #     self.col_current = 'current A'
    #     self.col_rpm = 'angVel rpm'
    #     self.col_temp = 'temp degC'
    #     self.col_warn = 'warning'
    #     self.col_inthtl = 'inthtl us'
    #     self.col_outthtl = 'outthtl perc'
    #
    #     self.time_win = time_win

    @staticmethod
    def get_pandas_dataframe(kdecan_file, time_win):
        # if verbose:
        #     print('[KdecanParser] Parsing file %s' % self.kdecan_file)
        dataframe = pandas.read_csv(
            kdecan_file, index_col=KdecanParser.col_time,
            parse_dates=True, skipinitialspace=True)
        dataframe = KdecanParser.apply_time_win(dataframe, time_win)
        # if verbose:
        #     print(dataframe)
        return dataframe

    @staticmethod
    def apply_time_win(dataframe, time_win):
        if (time_win is not None) and (len(time_win) == 2):
            time_win_0 = datetime.datetime.strptime(time_win[0])
            time_win_1 = datetime.datetime.strptime(time_win[0])
            # df = df.loc[time_win[0] < df.index < time_win[1]]
            dataframe = dataframe.loc[time_win_0 < dataframe.index]
            dataframe = dataframe.loc[dataframe.index < time_win_1]
        return dataframe

