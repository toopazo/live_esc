#!/usr/bin/python3

import os
import pandas
import datetime
import copy
from toopazo_tools.pandas import PandasTools


class KdecanParser:
    """
    Class to get data from log
    """

    def __init__(self):
        pass

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
        kdecan_df = pandas.read_csv(
            kdecan_file, index_col=KdecanParser.col_time,
            parse_dates=True, skipinitialspace=True)
        kdecan_df = PandasTools.apply_time_win_strptime(kdecan_df, time_win)
        # if verbose:
        #     print(dataframe)
        return kdecan_df

    @staticmethod
    def kdecan_df_to_escid_df(kdecan_df, escid):
        assert isinstance(kdecan_df, pandas.DataFrame)
        escid_cond = kdecan_df['escid'] == escid
        escid_df = kdecan_df[escid_cond]

        # escid_t0 = escid_df.index[0]
        # escid_tf = escid_df.index[-1]
        # escid_num_samples = len(escid_df.index)
        # escid_sample_period = escid_tf / escid_num_samples
        # print(f'escid {escid}')
        # print(f'escid_t0 {escid_t0}')
        # print(f'escid_tf {escid_tf}')
        # print(f'escid_num_samples {escid_num_samples}')
        # print(f'escid_sample_period {escid_sample_period}')

        data = {
            'voltage V': escid_df['voltage V'].values,
            'current A': escid_df['current A'].values,
            'angVel rpm': escid_df['angVel rpm'].values,
            'temp degC': escid_df['temp degC'].values,
            'warning': escid_df['warning'].values,
            'inthtl us': escid_df['inthtl us'].values,
            'outthtl perc': escid_df['outthtl perc'].values,
        }
        index = escid_df.index
        new_escid_df = pandas.DataFrame(data=data, index=index)

        # new_escid_t0 = new_escid_df.index[0]
        # new_escid_tf = new_escid_df.index[-1]
        # new_escid_num_samples = len(new_escid_df.index)
        # new_escid_sample_period = new_escid_tf / new_escid_num_samples
        # print(f'new_escid_t0 {new_escid_t0}')
        # print(f'new_escid_tf {new_escid_tf}')
        # print(f'new_escid_num_samples {new_escid_num_samples}')
        # print(f'new_escid_sample_period {new_escid_sample_period}')

        return copy.deepcopy(new_escid_df)

    @staticmethod
    def kdecan_df_to_escid_dict(kdecan_df):
        # Create new dataframes for each escid
        esc11_df = KdecanParser.kdecan_df_to_escid_df(kdecan_df, escid=11)
        esc12_df = KdecanParser.kdecan_df_to_escid_df(kdecan_df, escid=12)
        esc13_df = KdecanParser.kdecan_df_to_escid_df(kdecan_df, escid=13)
        esc14_df = KdecanParser.kdecan_df_to_escid_df(kdecan_df, escid=14)
        esc15_df = KdecanParser.kdecan_df_to_escid_df(kdecan_df, escid=15)
        esc16_df = KdecanParser.kdecan_df_to_escid_df(kdecan_df, escid=16)
        esc17_df = KdecanParser.kdecan_df_to_escid_df(kdecan_df, escid=17)
        esc18_df = KdecanParser.kdecan_df_to_escid_df(kdecan_df, escid=18)
        min_num_samples = min(
            esc11_df.shape[0], esc12_df.shape[0],
            esc13_df.shape[0], esc14_df.shape[0],
            esc15_df.shape[0], esc16_df.shape[0],
            esc17_df.shape[0], esc18_df.shape[0]
        )
        escid_dict = {
            'esc11_df': esc11_df.iloc[:min_num_samples],
            'esc12_df': esc12_df.iloc[:min_num_samples],
            'esc13_df': esc13_df.iloc[:min_num_samples],
            'esc14_df': esc14_df.iloc[:min_num_samples],
            'esc15_df': esc15_df.iloc[:min_num_samples],
            'esc16_df': esc16_df.iloc[:min_num_samples],
            'esc17_df': esc17_df.iloc[:min_num_samples],
            'esc18_df': esc18_df.iloc[:min_num_samples],
        }
        return copy.deepcopy(escid_dict)

