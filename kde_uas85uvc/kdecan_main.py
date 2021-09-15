#!/usr/bin/python3

# import can
# import signal
# import sys
# import os
import time
import datetime
from toopazo_tools.file_folder import FileFolderTools as FFTools
from kdecan_driver import KdeCanAPI, KdeCanLive
import sys
import subprocess


if __name__ == '__main__':
    ufolder = sys.argv[1]
    ufolder = FFTools.full_path(ufolder)
    print('target folder {}'.format(ufolder))
    if FFTools.is_folder(ufolder):
        cwd = FFTools.get_cwd()
        print('current folder {}'.format(cwd))
    else:
        arg = '{} is not a folder'.format(ufolder)
        raise RuntimeError(arg)

    # list_files = subprocess.run(["ls", "-l"])
    # print("returncode: {}".format(list_files.returncode))
    # print("stdout: {}".format(list_files.stdout))
    # print("args: {}".format(list_files.args))

    kdecanlive = KdeCanLive(ufolder)
    for uesc in range(11, 19):
        umsg = kdecanlive.kdecanapi.get_data_esc(uesc)
        umsg = kdecanlive.kdecanapi.data_esc_to_str(umsg)
        print(umsg)

    uesc_arr = list(range(11, 19))
    uperiod = 0.1
    kdecanlive.live_data(uesc_arr, uperiod)

