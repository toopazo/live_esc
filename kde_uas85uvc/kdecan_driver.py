#!/usr/bin/python3
import os

import can
import time
import numpy as np
import signal
import sys
import datetime
import subprocess
from kdecan_parseMsg import ParseMsg
from toopazo_tools.file_folder import FileFolderTools as FFTools


class KdeCanLive:
    def __init__(self, folder):
        # assert isinstance(kdecanapi, KdeCanAPI)
        self.kdecanapi = KdeCanAPI()

        # folder for logs
        self.folder = folder
        self.logs_in_folder = self.find_logs_in_folder()

        self.log_filename = None
        self.log_fd = None
        # log_141_2020-12-22-13-41-26.ulg
        self.log_filename_separator = '_'
        self.log_filename_logstr = 'log'
        self.log_filename_extension = 'kdecan'

        self.time0 = time.time()
        signal.signal(signal.SIGINT, self.signal_handler)

    def find_logs_in_folder(self):
        file_lognum_arr = []
        lognum_arr = []
        logdate_arr = []
        logname_arr = []

        farr = FFTools.get_file_arr(
            self.folder, extension=self.log_filename_extension)
        for file in farr:
            [head, tail] = FFTools.get_file_split(file)
            _ = head
            logname = tail
            res = self.parse_log_filename(logname)
            if res is not None:
                [logstr, lognum, logdate] = res
                _ = logstr
                file_lognum_arr.append(lognum)
                print('Detected log {} captured on {}, filename {}'.format(
                    lognum, logdate, logname))
                lognum_arr.append(lognum)
                logdate_arr.append(logdate)
                logname_arr.append(logname)

        logs_in_folder = {'folder': self.folder, 'lognum': lognum_arr,
                          'logdate': logdate_arr, 'logname': logname_arr}
        return logs_in_folder

    def parse_log_filename(self, filename):
        if self.log_filename_extension in filename:
            # log_141_2020-12-22-13-41-26.ulg
            tail = '.{}'.format(self.log_filename_extension)
            filename = filename.replace(tail, '')
            farr = filename.split(self.log_filename_separator)
            print(farr)
            logstr = farr[0] == self.log_filename_logstr
            lognum = int(farr[1])
            logdate = datetime.datetime.strptime(farr[2], '%Y-%m-%d-%H-%M-%S')
            if len(farr) != 3:
                return None
            else:
                # print([logstr, lognum, logdate])
                return [logstr, lognum, logdate]
        else:
            return None

    def new_log_filename(self):
        self.logs_in_folder = self.find_logs_in_folder()

        dtnow = datetime.datetime.now()
        logstr = self.log_filename_logstr
        lognum = str(np.max(self.logs_in_folder['lognum']) + 1)
        logdate = dtnow.strftime("%Y-%m-%d-%H-%M-%S")

        separator = self.log_filename_separator
        extension = self.log_filename_extension
        fnarr = [
            logstr, separator, lognum, separator, logdate, '.', extension
        ]
        log_filename = ''.join(fnarr)
        return log_filename

    def close_it_all(self):
        # Close file
        if self.log_fd is None:
            pass
        else:
            self.log_fd.close()

        # close can bus
        self.kdecanapi.kdecan_bus.shutdown()

    def signal_handler(self, _signal, _frame):
        print('[signal_handler] calling self.kdecan_bus.shutdown() ..')
        print(_signal)
        print(_frame)
        self.close_it_all()
        sys.exit(0)

    def busy_waiting(self, t0, period, dt):
        telap = time.time() - t0
        ncycles = int(telap / period)
        tf = ncycles*period + period
        # print("[busy_waiting] t0 %s" % t0)
        # print("[busy_waiting] tf %s" % tf)

        # Busy waiting while current time "ti" is less than final time "tf"
        telap = time.time() - t0
        while telap < tf:
            telap = time.time() - t0
            # print("[busy_waiting] telap %s" % telap)
            time.sleep(dt)

    def test_pwm(self):

        # resp = self.set_restartesc(targetid, kdecan_recv_timeout)
        # arg = "[test_pwm] restartesc %mysched " % resp
        # print(arg)
        # time.sleep(20)

        # esc_arr = [11, 12, 13, 14, 15, 16, 17, 18]
        esc_arr = [11, 16]

        # Spin motors
        # nesc = len(esc_arr)
        # throttle = 1300
        # throttle_arr = throttle * np.ones(nesc)
        # self.set_pwm_esc_arr(esc_arr, throttle_arr, kdecan_recv_timeout)

        # Write first line of csv file
        arg = "time mysched, escid, " \
              "voltage V, current A, angVel rpm, temp degC, warning, " \
              "inthtl us, outthtl perc"
        print(arg)
        self.log_fd.write(arg + "\r\n")

        # Perform test
        niter = 0
        sampling_delay = 0.1
        # while niter <= 10:
        while True:
            niter = niter + 1

            resp_arr = self.kdecanapi.get_data_esc_arr(esc_arr)

            # for each targetid
            for resp in resp_arr:
                print(resp)
                [telap, targetid,
                 voltage, current, rpm, temp, warning,
                 inthrottle, outthrottle] = resp

                arg = "%s, %s, %04.2f, %s, %07.2f, %s, %s, %s, %s " % \
                      (telap, targetid,
                       voltage, current, rpm, temp, warning,
                       inthrottle, outthrottle)
                print(arg)
                self.log_fd.write(arg + "\r\n")

            # throttle = 1100 + niter * 70
            # throttle_arr = throttle*np.ones(nesc)
            # self.set_pwm_esc_arr(esc_arr, throttle_arr, kdecan_recv_timeout)

            self.busy_waiting(self.time0, 0.1, 0.01)

        # Terminate, if out of while loop
        # self.close_it_all()

    def live_data(self, esc_arr, sampling_period):
        # Open file
        self.log_filename = self.new_log_filename()
        self.log_fd = open(self.log_filename, "w")

        # Write first line of csv file
        arg = "time s, escid, " \
              "voltage V, current A, angVel rpm, temp degC, warning, " \
              "inthtl us, outthtl perc"
        print(arg)
        self.log_fd.write(arg + "\r\n")

        # Perform test
        # niter = 0
        # while niter <= 10:
        #     niter = niter + 1
        while True:
            # get data
            resp_arr = self.kdecanapi.get_data_esc_arr(esc_arr)

            # for each targetid, save data to file
            for resp in resp_arr:
                [telap, targetid,
                 voltage, current, rpm, temp, warning,
                 inthrottle, outthrottle] = resp

                #   arg = "%s, %s, %04.2f, %s, %07.2f, %s, %s, %s, %s " % \
                arg = "%s s, %s escid, " \
                      "%04.2f V, %s A, %07.2f rpm, %s degC, %s, " \
                      "%s us, %s perc " % \
                      (telap, targetid,
                       voltage, current, rpm, temp, warning,
                       inthrottle, outthrottle)
                print(arg)
                self.log_fd.write(arg + "\r\n")

            # busy wait for next loop
            self.busy_waiting(self.time0, sampling_period, sampling_period / 8)

        # # Terminate, if out of while loop
        # self.close_it_all()


class KdeCanAPI:

    def __init__(self):
        # sudo /sbin/ip link set can0 down
        # sudo /sbin/ip link set can0 up type can bitrate 500000
        # This last line was added to "/etc/rc.local" file

        # os.system('sudo ip link set can0 down')
        # os.system('sudo ip link set can0 type can bitrate 500000')
        # os.system('sudo ip link set can0 up')

        # self.check_can0_status()

        # create a kdecan_bus instance
        # many other interfaces are supported as well (see below)
        self.kdecan_bus = can.Bus(
            interface='socketcan', channel='can0', receive_own_messages=False,
            is_extended_id=True)
        self.kdecan_recv_timeout = 1    # 0.5
        self.kdecan_send_timeout = 0.2  # 0.5

    @staticmethod
    def check_can0_status():
        list_files = subprocess.Popen(["ifconfig", '-a'],
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True)
        list_files.wait()
        list_files.poll()
        # retcode = list_files.returncode
        results = list_files.stdout.read()
        # print("returncode: {}".format(retcode))
        # print("stdout: {}".format(results))
        results = results.split('\n')
        results = [i.strip() for i in results]
        # print(results)

        can0_pattern1 = 'can0:'
        can0_pattern2 = 'flags=128<NOARP>'
        can0_pattern3 = 'flags=193<UP,RUNNING,NOARP>'

        can0_up_running_noarpm = False
        for line in results:
            if can0_pattern1 in line:
                print(line)
                if can0_pattern2 in line:
                    can0_up_running_noarpm = False
                if can0_pattern3 in line:
                    can0_up_running_noarpm = True

        # can0: flags=128<NOARP>  mtu 16
        #         unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 10  (UNSPEC)
        #         RX packets 0  bytes 0 (0.0 B)
        #         RX errors 0  dropped 0  overruns 0  frame 0
        #         TX packets 0  bytes 0 (0.0 B)
        #         TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

        # os.system('sudo ip link set can0 down')
        # os.system('sudo ip link set can0 type can bitrate 500000')
        # os.system('sudo ip link set can0 up')

        # can0: flags=193<UP,RUNNING,NOARP>  mtu 16
        #         unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 10  (UNSPEC)
        #         RX packets 0  bytes 0 (0.0 B)
        #         RX errors 0  dropped 0  overruns 0  frame 0
        #         TX packets 0  bytes 0 (0.0 B)
        #         TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

        return can0_up_running_noarpm

    def set_pwm_esc_arr(self, esc_arr, throttle_arr):
        for i in range(0, len(esc_arr)):
            targetid = esc_arr[i]
            throttle = throttle_arr[i]
            self.set_pwm(throttle, targetid)

    def get_data_esc(self, targetid):
        # telap = round(time.time() - self.time0, 4)
        trecv = datetime.datetime.now()

        [voltage, current, rpm, temp, warning] = self.get_vcrtw(targetid)
        inthrottle = self.get_inputthrottle(targetid)
        outthrottle = self.get_outputthrottle(targetid)
        # self.get_mcuid(targetid)

        # resp = [telap, targetid,
        #         voltage, current, rpm, temp, warning,
        #         inthrottle, outthrottle]

        resp = [trecv, targetid,
                voltage, current, rpm, temp, warning,
                inthrottle, outthrottle]
        return resp

    def get_data_esc_header(self):
        arg = "time, escid, voltage, current, rpm, temp, warn, thtl_in, thtl_out"
        units = "s, escid, V, A, rpm, degC, str, us, %s perc "
        return arg

    def data_esc_to_str(self, resp):
        [telap, targetid,
         voltage, current, rpm, temp, warning,
         inthrottle, outthrottle] = resp

        #   arg = "%s, %s, %04.2f, %s, %07.2f, %s, %s, %s, %s " % \
        arg = "%s s, %s escid, " \
              "%04.2f V, %s A, %07.2f rpm, %s degC, %s, " \
              "%s us, %s perc " % \
              (telap, targetid,
               voltage, current, rpm, temp, warning,
               inthrottle, outthrottle)
        return arg

    def get_data_esc_arr(self, esc_arr):
        resp_arr = []
        for targetid in esc_arr:
            resp = self.get_data_esc(targetid)
            resp_arr.append(resp)

        return resp_arr

    def get_message(self, targetid, objctadd, data_arr):
        # CAN Bus Extended Frame Structure (CAN 2.0B)
        # A kdecan_bus frame consists of an extended frame ID and a data frame.
        # The extended frame ID consists of 5 bits for priority, 8 bits for the
        # source id (sender), 8 bits for the destination id (receiver),
        # and 8 bits for the object address which tells the ESC how to respond
        # to the message.

        # priority = "%02X" % 0    # "{0:05b}".format(0)  # '01011'
        # print("priority = %mysched" % priority)
        #
        # sourceid = "%02X" % 0    # "{0:08b}".format(0)
        # print("sourceid = %mysched" % sourceid)
        #
        # targetid = "%02X" % 17    # "{0:08b}".format(1)
        # print("targetid = %mysched" % targetid)
        #
        # objctadd = "%02X" % 2    # "{0:08b}".format(2)
        # print("objctadd = %mysched" % objctadd)
        #
        # arbitrid = priority + sourceid + targetid + objctadd
        # print("arbitrid = %mysched" % arbitrid)
        #
        # arbitrid = int(arbitrid, 16)
        # # print("arbitrid = 43210765432107654321076543210")
        # print("arbitrid = {0:029b}".format(arbitrid))

        # %d - print in integer format.
        # %o - print in octal format.
        # %x - print in hexadecimal format (letters will print in lowercase)
        # %X - print in hexadecimal format (letters will print in uppercase)

        priority = "%02X" % 0
        sourceid = "%02X" % 0
        targetid = "%02X" % targetid
        objctadd = "%02X" % objctadd

        # convert "arbitrid" into an integer with base 16 (hexadecimal)
        arbitrid = priority + sourceid + targetid + objctadd
        arbitrid = int(arbitrid, 16)

        # send a message
        # message = can.Message(arbitration_id=arbitrid, is_extended_id=True,
        #                       data=data_arr)
        message = can.Message(arbitration_id=arbitrid, data=data_arr)

        return message

    def check_recv_msg(self, msg, targetid, objctadd):
        try:
            arbitration_id = msg.arbitration_id
        except AttributeError:
            arg = "[check_recv_msg] targetid %s: No recv msg for objctadd %s" \
                  % (targetid, objctadd)
            print(arg)
            return False

        [_priority, _sourceid, _targetid, _objctadd] = ParseMsg.parse_arbitrid(
            arbitration_id)

        if (targetid != _sourceid) or (objctadd != _objctadd):
            arg = "[check_recv_msg] targetid %s: Wrong msg for objctadd %s" \
                  % (targetid, objctadd)
            print(arg)
            return False
        else:
            return True

    def get_esc_info(self, targetid):
        objctadd = 0x00
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = self.get_message(targetid, objctadd, data_arr)

        # self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        # # iterate over received messages
        # t0 = time.time()
        # for msg in self.kdecan_bus:
        #     voltage = self.parse_voltage(msg)
        #     telapsed = time.time() - t0
        #     time.sleep(1)
        #     print("[get_voltage] telapsed %mysched " % telapsed)
        #     if telapsed >= timeout:
        #         return voltage

        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        self.check_recv_msg(msg, targetid, objctadd)
        return ParseMsg.parse_esc_info(msg)

    def set_pwm(self, throttle, targetid):
        objctadd = 0x01
        # data_arr = [0x05, 0xFC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        data_arr = ParseMsg.uint16_to_bytearray(np.uint16(throttle))
        message = self.get_message(targetid, objctadd, data_arr)
        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        # msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        # self.check_recv_msg(msg, targetid, objctadd)
        # return ParseMsg.parse_pwm(msg)

    def get_voltage(self, targetid):
        objctadd = 0x02
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = self.get_message(targetid, objctadd, data_arr)

        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        self.check_recv_msg(msg, targetid, objctadd)
        return ParseMsg.parse_voltage(msg)

    def get_current(self, targetid):
        objctadd = 0x03
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = self.get_message(targetid, objctadd, data_arr)

        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        self.check_recv_msg(msg, targetid, objctadd)
        return ParseMsg.parse_current(msg)

    @staticmethod
    def get_currentbias(targetid):
        if targetid == 11:
            return 7.66
        if targetid == 12:
            return 3.32
        if targetid == 13:
            return 1.00
        if targetid == 14:
            return 1.65
        if targetid == 15:
            return 7.51
        if targetid == 16:
            return 4.19
        if targetid == 17:
            return 1.00
        if targetid == 18:
            return 1.00

    def get_rpm(self, targetid):
        objctadd = 0x04
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = self.get_message(targetid, objctadd, data_arr)

        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        self.check_recv_msg(msg, targetid, objctadd)
        return ParseMsg.parse_rpm(msg)

    def get_temperature(self, targetid):
        objctadd = 0x05
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = self.get_message(targetid, objctadd, data_arr)

        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        self.check_recv_msg(msg, targetid, objctadd)
        return ParseMsg.parse_temperature(msg)

    def get_inputthrottle(self, targetid):
        objctadd = 0x06
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = self.get_message(targetid, objctadd, data_arr)

        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        msg = self.kdecan_bus.recv(self.kdecan_recv_timeout)
        self.check_recv_msg(msg, targetid, objctadd)
        return ParseMsg.parse_inputthrottle(msg)

    def get_outputthrottle(self, targetid):
        objctadd = 0x07
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = self.get_message(targetid, objctadd, data_arr)

        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        self.check_recv_msg(msg, targetid, objctadd)
        return ParseMsg.parse_outputthrottle(msg)

    def get_mcuid(self, targetid):
        objctadd = 0x08
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = self.get_message(targetid, objctadd, data_arr)

        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        self.check_recv_msg(msg, targetid, objctadd)
        return ParseMsg.parse_mcuid(msg)

    def get_vcrtw(self, targetid):
        objctadd = 0x0B     # 0x0B = 11
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = self.get_message(targetid, objctadd, data_arr)

        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        self.check_recv_msg(msg, targetid, objctadd)
        return ParseMsg.parse_vcrtw(msg)

    def set_turnoffesc(self, targetid):
        objctadd = 0x20
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = self.get_message(targetid, objctadd, data_arr)

        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        self.check_recv_msg(msg, targetid, objctadd)
        return ParseMsg.parse_turnoffesc(msg)

    def set_restartesc(self, targetid):
        objctadd = 0x21
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = self.get_message(targetid, objctadd, data_arr)

        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        self.check_recv_msg(msg, targetid, objctadd)
        return ParseMsg.parse_restartesc(msg)
