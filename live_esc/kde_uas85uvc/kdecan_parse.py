#!/usr/bin/python3

import os
import pandas
import numpy as np
import copy
from toopazo_tools.pandas import PandasTools, DataframeTools


class KdecanParser:
    """
    Class to get data from log
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

    def __init__(self):
        pass

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
    def get_escid_dict(kdecan_file):
        kdecan_df = KdecanParser.get_pandas_dataframe(
            kdecan_file, time_win=None)
        escid_dict = KdecanParser.kdecan_df_to_escid_dict(kdecan_df)
        return escid_dict

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


class EscidParserTools:
    @staticmethod
    def get_arm_dict(escid_dict):
        esc11_df = escid_dict['esc11_df']
        esc12_df = escid_dict['esc12_df']
        esc13_df = escid_dict['esc13_df']
        esc14_df = escid_dict['esc14_df']
        esc15_df = escid_dict['esc15_df']
        esc16_df = escid_dict['esc16_df']
        esc17_df = escid_dict['esc17_df']
        esc18_df = escid_dict['esc18_df']

        esc11_power = esc11_df[KdecanParser.col_voltage].values * esc11_df[
            KdecanParser.col_current].values
        esc12_power = esc12_df[KdecanParser.col_voltage].values * esc12_df[
            KdecanParser.col_current].values
        esc13_power = esc13_df[KdecanParser.col_voltage].values * esc13_df[
            KdecanParser.col_current].values
        esc14_power = esc14_df[KdecanParser.col_voltage].values * esc14_df[
            KdecanParser.col_current].values
        esc15_power = esc15_df[KdecanParser.col_voltage].values * esc15_df[
            KdecanParser.col_current].values
        esc16_power = esc16_df[KdecanParser.col_voltage].values * esc16_df[
            KdecanParser.col_current].values
        esc17_power = esc17_df[KdecanParser.col_voltage].values * esc17_df[
            KdecanParser.col_current].values
        esc18_power = esc18_df[KdecanParser.col_voltage].values * esc18_df[
            KdecanParser.col_current].values

        arm1_power = esc11_power + esc16_power
        arm2_power = esc12_power + esc15_power
        arm3_power = esc13_power + esc18_power
        arm4_power = esc14_power + esc17_power

        arm1_eta_angvel = esc11_df[KdecanParser.col_rpm].values / esc16_df[
            KdecanParser.col_rpm].values
        arm2_eta_angvel = esc12_df[KdecanParser.col_rpm].values / esc15_df[
            KdecanParser.col_rpm].values
        arm3_eta_angvel = esc13_df[KdecanParser.col_rpm].values / esc18_df[
            KdecanParser.col_rpm].values
        arm4_eta_angvel = esc14_df[KdecanParser.col_rpm].values / esc17_df[
            KdecanParser.col_rpm].values

        arm1_eta_throttle = esc11_df[KdecanParser.col_inthtl].values / esc16_df[
            KdecanParser.col_inthtl].values
        arm2_eta_throttle = esc12_df[KdecanParser.col_inthtl].values / esc15_df[
            KdecanParser.col_inthtl].values
        arm3_eta_throttle = esc13_df[KdecanParser.col_inthtl].values / esc18_df[
            KdecanParser.col_inthtl].values
        arm4_eta_throttle = esc14_df[KdecanParser.col_inthtl].values / esc17_df[
            KdecanParser.col_inthtl].values

        arm_dict = {
            'arm1': [arm1_power, arm1_eta_angvel, arm1_eta_throttle],
            'arm2': [arm2_power, arm2_eta_angvel, arm2_eta_throttle],
            'arm3': [arm3_power, arm3_eta_angvel, arm3_eta_throttle],
            'arm4': [arm4_power, arm4_eta_angvel, arm4_eta_throttle],
        }
        return arm_dict

    @staticmethod
    def resample(escid_dict, time_secs, max_delta):
        if DataframeTools.check_time_difference(escid_dict, max_delta):
            # time_secs = DataframeTools.shortest_time_secs(escid_dict)
            pass
        else:
            raise RuntimeError('EscidParserTools.check_time_difference failed')

        new_escid_dict = {}
        x = time_secs
        for key, escid_df in escid_dict.items():
            # xp = escid_df.index
            xp = DataframeTools.index_to_elapsed_time(escid_df)
            data = {
                'voltage V':  np.interp(x, xp, fp=escid_df['voltage V']),
                'current A':  np.interp(x, xp, fp=escid_df['current A']),
                'angVel rpm': np.interp(x, xp, fp=escid_df['angVel rpm']),
                'temp degC': np.interp(x, xp, fp=escid_df['temp degC']),
                'inthtl us': np.interp(x, xp, fp=escid_df['inthtl us']),
                'outthtl perc': np.interp(x, xp, fp=escid_df['outthtl perc']),
            }
            index = x
            new_escid_df = pandas.DataFrame(data=data, index=index)
            new_escid_dict[key] = new_escid_df
            # print(f"key {key} ------------------------")
            # print(f"{escid_df}")
            # print(f"{new_escid_df}")
        return copy.deepcopy(new_escid_dict)

    @staticmethod
    def synchronize(escid_dict, time_secs):
        max_delta = 0.01
        if DataframeTools.check_time_difference(escid_dict, max_delta):
            # time_secs = DataframeTools.shortest_time_secs(escid_dict)
            new_escid_dict = EscidParserTools.resample(
                escid_dict, time_secs, max_delta)
            return copy.deepcopy(new_escid_dict)
        else:
            raise RuntimeError('EscidParserTools.check_time_difference failed')

    @staticmethod
    def remove_by_condition(escid_dict, escid_ref_cond):
        # assert isinstance(kdecan_df, pandas.DataFrame)
        # assert isinstance(ulg_out_df, pandas.DataFrame)

        esc11_df = escid_dict['esc11_df']
        esc12_df = escid_dict['esc12_df']
        esc13_df = escid_dict['esc13_df']
        esc14_df = escid_dict['esc14_df']
        esc15_df = escid_dict['esc15_df']
        esc16_df = escid_dict['esc16_df']
        esc17_df = escid_dict['esc17_df']
        esc18_df = escid_dict['esc18_df']

        # escid_df = escid_dict[f'esc{reference_escid}_df']
        # escid_ref_cond = escid_df['inthtl us'] > min_throttle

        escid_ref_cond.index = esc11_df.index
        esc11_df = esc11_df[escid_ref_cond]
        escid_ref_cond.index = esc12_df.index
        esc12_df = esc12_df[escid_ref_cond]
        escid_ref_cond.index = esc13_df.index
        esc13_df = esc13_df[escid_ref_cond]
        escid_ref_cond.index = esc14_df.index
        esc14_df = esc14_df[escid_ref_cond]
        escid_ref_cond.index = esc15_df.index
        esc15_df = esc15_df[escid_ref_cond]
        escid_ref_cond.index = esc16_df.index
        esc16_df = esc16_df[escid_ref_cond]
        escid_ref_cond.index = esc17_df.index
        esc17_df = esc17_df[escid_ref_cond]
        escid_ref_cond.index = esc18_df.index
        esc18_df = esc18_df[escid_ref_cond]

        escid_dict = {
            'esc11_df': esc11_df,
            'esc12_df': esc12_df,
            'esc13_df': esc13_df,
            'esc14_df': esc14_df,
            'esc15_df': esc15_df,
            'esc16_df': esc16_df,
            'esc17_df': esc17_df,
            'esc18_df': esc18_df,
        }

        return copy.deepcopy(escid_dict)
