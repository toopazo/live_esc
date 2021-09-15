#!/usr/bin/python3

import sys
import numpy as np
import signal
import time
import datetime
from toopazo_tools.file_folder import FileFolderTools as FFTools
from toopazo_tools.telemetry import TelemetryLogger
from kdecan_interface import KdeCanIface


# class KdeCanLive:
#     def __init__(self, folder):
#         # assert isinstance(kdecanapi, KdeCanAPI)
#         self.kdecanapi = KdeCanAPI()
#
#         self.log_filename = None
#         self.log_fd = None
#         # log_141_2020-12-22-13-41-26.ulg
#         self.log_filename_separator = '_'
#         self.log_filename_logstr = 'log'
#         self.log_filename_extension = '.kdecan'
#
#         # folder for logs
#         self.log_folder = folder
#         self.logs_in_folder = self.find_logs_in_folder()
#
#         self.time0 = time.time()
#         signal.signal(signal.SIGINT, self.signal_handler)
#
#     def find_logs_in_folder(self):
#         file_lognum_arr = []
#         lognum_arr = []
#         logdate_arr = []
#         logname_arr = []
#
#         farr = FFTools.get_file_arr(
#             self.log_folder, extension=self.log_filename_extension)
#         for file in farr:
#             [head, tail] = FFTools.get_file_split(file)
#             _ = head
#             logname = tail
#             res = self.parse_log_filename(logname)
#             if res is not None:
#                 [logstr, lognum, logdate] = res
#                 _ = logstr
#                 file_lognum_arr.append(lognum)
#                 print('[find_logs_in_folder] lognum {}, logdate  {}, logname {}'
#                       .format(lognum, logdate, logname))
#                 lognum_arr.append(lognum)
#                 logdate_arr.append(logdate)
#                 logname_arr.append(logname)
#
#         logs_in_folder = {'folder': self.log_folder, 'lognum': lognum_arr,
#                           'logdate': logdate_arr, 'logname': logname_arr}
#         return logs_in_folder
#
#     def parse_log_filename(self, filename):
#         if self.log_filename_extension in filename:
#             # log_141_2020-12-22-13-41-26.ulg
#             filename = filename.replace(self.log_filename_extension, '')
#             farr = filename.split(self.log_filename_separator)
#
#             print('[parse_log_filename] filename {}'.format(filename))
#             print('[parse_log_filename] farr {}'.format(farr))
#             logstr = farr[0] == self.log_filename_logstr
#             lognum = int(farr[1])
#             logdate = datetime.datetime.strptime(farr[2], '%Y-%m-%d-%H-%M-%S')
#
#             if len(farr) != 3:
#                 return None
#             else:
#                 # print([logstr, lognum, logdate])
#                 return [logstr, lognum, logdate]
#         else:
#             return None
#
#     def new_log_filename(self):
#         self.logs_in_folder = self.find_logs_in_folder()
#         if len(self.logs_in_folder['lognum']) > 0:
#             prev_lognum = np.max(self.logs_in_folder['lognum'])
#         else:
#             prev_lognum = 0
#
#         dtnow = datetime.datetime.now()
#         logstr = self.log_filename_logstr
#         lognum = str(prev_lognum + 1)
#         logdate = dtnow.strftime("%Y-%m-%d-%H-%M-%S")
#
#         separator = self.log_filename_separator
#         extension = self.log_filename_extension
#         fnarr = [
#             logstr, separator, lognum, separator, logdate, extension
#         ]
#         log_filename = ''.join(fnarr)
#         return log_filename
#
#     def close_it_all(self):
#         # Close file
#         if self.log_fd is None:
#             pass
#         else:
#             self.log_fd.close()
#
#         # close can bus
#         self.kdecanapi.kdecan_bus.shutdown()
#
#     def signal_handler(self, _signal, _frame):
#         print('[signal_handler] calling self.kdecan_bus.shutdown() ..')
#         print('[signal_handler] signal {}'.format(_signal))
#         print('[signal_handler] frame  {}'.format(_frame))
#         self.close_it_all()
#         sys.exit(0)
#
#     @staticmethod
#     def busy_waiting(t0, period, dt):
#         telap = time.time() - t0
#         ncycles = int(telap / period)
#         tf = ncycles*period + period
#         # print("[busy_waiting] t0 %s" % t0)
#         # print("[busy_waiting] tf %s" % tf)
#
#         # Busy waiting while current time "ti" is less than final time "tf"
#         telap = time.time() - t0
#         while telap < tf:
#             telap = time.time() - t0
#             # print("[busy_waiting] telap %s" % telap)
#             time.sleep(dt)
#
#     def test_pwm(self):
#
#         # resp = self.set_restartesc(targetid, kdecan_recv_timeout)
#         # arg = "[test_pwm] restartesc %mysched " % resp
#         # print(arg)
#         # time.sleep(20)
#
#         # esc_arr = [11, 12, 13, 14, 15, 16, 17, 18]
#         esc_arr = [11, 16]
#
#         # Spin motors
#         # nesc = len(esc_arr)
#         # throttle = 1300
#         # throttle_arr = throttle * np.ones(nesc)
#         # self.set_pwm_esc_arr(esc_arr, throttle_arr, kdecan_recv_timeout)
#
#         # Write first line of csv file
#         arg = "time mysched, escid, " \
#               "voltage V, current A, angVel rpm, temp degC, warning, " \
#               "inthtl us, outthtl perc"
#         print(arg)
#         self.log_fd.write(arg + "\r\n")
#
#         # Perform test
#         niter = 0
#         sampling_delay = 0.1
#         # while niter <= 10:
#         while True:
#             niter = niter + 1
#
#             resp_arr = self.kdecanapi.get_data_esc_arr(esc_arr)
#
#             # for each targetid
#             for resp in resp_arr:
#                 print(resp)
#                 [telap, targetid,
#                  voltage, current, rpm, temp, warning,
#                  inthrottle, outthrottle] = resp
#
#                 arg = "%s, %s, %04.2f, %s, %07.2f, %s, %s, %s, %s " % \
#                       (telap, targetid,
#                        voltage, current, rpm, temp, warning,
#                        inthrottle, outthrottle)
#                 print(arg)
#                 self.log_fd.write(arg + "\r\n")
#
#             # throttle = 1100 + niter * 70
#             # throttle_arr = throttle*np.ones(nesc)
#             # self.set_pwm_esc_arr(esc_arr, throttle_arr, kdecan_recv_timeout)
#
#             KdeCanLive.busy_waiting(self.time0, 0.1, 0.01)
#
#         # Terminate, if out of while loop
#         # self.close_it_all()
#
#     def live_data(self, esc_arr, sampling_period):
#         # Open file
#         self.log_filename = self.new_log_filename()
#         self.log_fd = open(self.log_filename, "w")
#
#         # Write first line of csv file
#         log_header = "time s, escid, " \
#                      "voltage V, current A, angVel rpm, temp degC, warning, " \
#                      "inthtl us, outthtl perc"
#         print(log_header)
#         self.log_fd.write(log_header + "\r\n")
#
#         # Perform test
#         # niter = 0
#         # while niter <= 10:
#         #     niter = niter + 1
#         while True:
#             # get data
#             resp_arr = self.kdecanapi.get_data_esc_arr(esc_arr)
#
#             # for each targetid, save data to file
#             for resp in resp_arr:
#                 [telap, targetid,
#                  voltage, current, rpm, temp, warning,
#                  inthrottle, outthrottle] = resp
#
#                 log_data = "%s, %s, %04.2f, %s, %07.2f, %s, %s, %s, %s " % \
#                            (telap, targetid,
#                             voltage, current, rpm, temp, warning,
#                             inthrottle, outthrottle)
#                 # log_data = "%s s, %s escid, " \
#                 #       "%04.2f V, %s A, %07.2f rpm, %s degC, %s, " \
#                 #       "%s us, %s perc " % \
#                 #       (telap, targetid,
#                 #        voltage, current, rpm, temp, warning,
#                 #        inthrottle, outthrottle)
#                 print(log_data)
#                 self.log_fd.write(log_data + "\r\n")
#
#             # busy wait for next loop
#             KdeCanLive.busy_waiting(self.time0, sampling_period, sampling_period / 8)
#
#         # # Terminate, if out of while loop
#         # self.close_it_all()


class KdeCanIfaceWrapper:
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
            # log_data = "%s s, %s escid, " \
            #       "%04.2f V, %s A, %07.2f rpm, %s degC, %s, " \
            #       "%s us, %s perc " % \
            #       (telap, targetid,
            #        voltage, current, rpm, temp, warning,
            #        inthrottle, outthrottle)
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
    utelemetry_iface = KdeCanIfaceWrapper()
    utelemetry_ext = ".kdecan"
    telem_logger = TelemetryLogger(ufolder, utelemetry_iface, utelemetry_ext)

    usampling_period = 0.1
    ulog_header = "time s, escid, "\
                  "voltage V, current A, angVel rpm, temp degC, warning, " \
                  "inthtl us, outthtl perc"
    telem_logger.live_data(usampling_period, ulog_header)

