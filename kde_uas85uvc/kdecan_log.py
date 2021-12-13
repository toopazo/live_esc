#!/usr/bin/python3

import sys
# import numpy as np
# import signal
# import time
# import datetime
from toopazo_tools.file_folder import FileFolderTools as FFTools
from toopazo_tools.telemetry import TelemetryLogger
from kdecan_interface import KdeCanIface


class KdecanIfaceWrapper:
    def __init__(self):
        self.kdecan = KdeCanIface()
        self.esc_arr = list(range(11, 19))

    def get_data(self):
        # get data
        resp_arr = self.kdecan.get_data_esc_arr(self.esc_arr)

        # for each targetid, get data
        log_data_final = ""
        for resp in resp_arr:
            [telap, targetid,
             voltage, current, rpm, temp, warning,
             inthrottle, outthrottle] = resp

            log_data = "%s, %s, %04.2f, %s, %07.2f, %s, %s, %s, %s " % \
                       (telap, targetid,
                        voltage, current, rpm, temp, warning,
                        inthrottle, outthrottle)
            if len(log_data_final) == 0:
                log_data_final = log_data
            else:
                log_data_final = log_data_final + "\r\n" + log_data
            # self.log_fd.write(log_data + "\r\n")
        return log_data_final

    def close(self):
        self.kdecan.kdecan_bus.shutdown()


def parse_user_arg(folder):
    folder = FFTools.full_path(folder)
    print('target folder {}'.format(folder))
    if FFTools.is_folder(folder):
        cwd = FFTools.get_cwd()
        print('current folder {}'.format(cwd))
    else:
        arg = '{} is not a folder'.format(folder)
        raise RuntimeError(arg)
    return folder


if __name__ == '__main__':
    ufolder = sys.argv[1]
    ufolder = parse_user_arg(ufolder)

    # kdecanlive = KdeCanLive(ufolder)
    kdecanapi = KdeCanIface()
    for uesc in range(11, 19):
        umsg = kdecanapi.get_data_esc(uesc)
        umsg = kdecanapi.data_esc_to_str(umsg)
        print(umsg)

    ufolder = ufolder
    utelemetry_iface = KdecanIfaceWrapper()
    utelemetry_ext = ".kdecan"
    telem_logger = TelemetryLogger(ufolder, utelemetry_iface, utelemetry_ext)

    usampling_period = 0.1
    ulog_header = "time s, escid, "\
                  "voltage V, current A, angVel rpm, temp degC, warning, " \
                  "inthtl us, outthtl perc"
    telem_logger.live_data(usampling_period, ulog_header)

