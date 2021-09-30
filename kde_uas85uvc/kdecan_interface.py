#!/usr/bin/python3

import os
import can
import numpy as np
import datetime
import subprocess


class KdeCanIface:

    def __init__(self):
        if self.check_can0_status():
            pass
        else:
            os.system('sudo ip link set can0 down')
            os.system('sudo ip link set can0 type can bitrate 500000')
            os.system('sudo ip link set can0 up')

        # create a kdecan_bus instance
        self.kdecan_bus = can.Bus(
            interface='socketcan', channel='can0', receive_own_messages=False,
            is_extended_id=True)
        self.kdecan_recv_timeout = 1    # 0.5
        self.kdecan_send_timeout = 0.2  # 0.5
        self.kdecan_max_num_tries = 5

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

        can0_up_running_noarp = False
        for line in results:
            if can0_pattern1 in line:
                print("[check_can0_status] ".format(line))
                if can0_pattern2 in line:
                    can0_up_running_noarp = False
                if can0_pattern3 in line:
                    can0_up_running_noarp = True

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

        return can0_up_running_noarp

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

    def data_esc_to_str(self, resp):
        [telap, targetid,
         voltage, current, rpm, temp, warning,
         inthrottle, outthrottle] = resp

        #   arg = "%s, %s, %04.2f, %s, %07.2f, %s, %s, %s, %s " % \
        arg = "%s time, %s escid, " \
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

    @staticmethod
    def assemble_can_message(targetid, objctadd, data_arr):
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

    @staticmethod
    def check_recv_msg(msg, targetid, objctadd):
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

    def robust_msg_transmition(self, message, targetid, objctadd):
        # self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        # msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        # self.check_recv_msg(msg, targetid, objctadd)
        # return ParseMsg.parse_current(msg)

        # self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        # msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        # self.check_recv_msg(msg, targetid, objctadd)
        # return ParseMsg.parse_restartesc(msg)

        for i in range(0, self.kdecan_max_num_tries):
            self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
            msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
            if KdeCanIface.check_recv_msg(msg, targetid, objctadd):
                return ParseMsg.parse_recv_msg(msg, objctadd)
        return None

    def get_esc_info(self, targetid):
        objctadd = 0x00
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = KdeCanIface.assemble_can_message(targetid, objctadd, data_arr)
        return self.robust_msg_transmition(message, targetid, objctadd)

    def get_voltage(self, targetid):
        objctadd = 0x02
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = KdeCanIface.assemble_can_message(targetid, objctadd, data_arr)
        return self.robust_msg_transmition(message, targetid, objctadd)

    def get_current(self, targetid):
        objctadd = 0x03
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = KdeCanIface.assemble_can_message(targetid, objctadd, data_arr)
        return self.robust_msg_transmition(message, targetid, objctadd)

    def get_rpm(self, targetid):
        objctadd = 0x04
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = KdeCanIface.assemble_can_message(targetid, objctadd, data_arr)
        return self.robust_msg_transmition(message, targetid, objctadd)

    def get_temperature(self, targetid):
        objctadd = 0x05
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = KdeCanIface.assemble_can_message(targetid, objctadd, data_arr)
        return self.robust_msg_transmition(message, targetid, objctadd)

    def get_inputthrottle(self, targetid):
        objctadd = 0x06
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = KdeCanIface.assemble_can_message(targetid, objctadd, data_arr)
        return self.robust_msg_transmition(message, targetid, objctadd)

    def get_outputthrottle(self, targetid):
        objctadd = 0x07
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = KdeCanIface.assemble_can_message(targetid, objctadd, data_arr)
        return self.robust_msg_transmition(message, targetid, objctadd)

    def get_mcuid(self, targetid):
        objctadd = 0x08
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = KdeCanIface.assemble_can_message(targetid, objctadd, data_arr)
        return self.robust_msg_transmition(message, targetid, objctadd)

    def get_vcrtw(self, targetid):
        objctadd = 0x0B     # 0x0B = 11
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = KdeCanIface.assemble_can_message(targetid, objctadd, data_arr)
        return self.robust_msg_transmition(message, targetid, objctadd)

    def set_pwm(self, throttle, targetid):
        objctadd = 0x01
        # data_arr = [0x05, 0xFC, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        data_arr = ParseMsg.uint16_to_bytearray(np.uint16(throttle))
        message = KdeCanIface.assemble_can_message(targetid, objctadd, data_arr)
        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        # msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        # self.check_recv_msg(msg, targetid, objctadd)
        # return ParseMsg.parse_pwm(msg)

    def set_turnoffesc(self, targetid):
        objctadd = 0x20
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = KdeCanIface.assemble_can_message(targetid, objctadd, data_arr)
        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        # msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        # self.check_recv_msg(msg, targetid, objctadd)
        # return ParseMsg.parse_pwm(msg)

    def set_restartesc(self, targetid):
        objctadd = 0x21
        data_arr = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        message = KdeCanIface.assemble_can_message(targetid, objctadd, data_arr)
        self.kdecan_bus.send(message, timeout=self.kdecan_send_timeout)
        # msg = self.kdecan_bus.recv(timeout=self.kdecan_recv_timeout)
        # self.check_recv_msg(msg, targetid, objctadd)
        # return ParseMsg.parse_pwm(msg)


class ParseMsg:
    @staticmethod
    def uint16_to_bytearray(uint16):
        isinstance(uint16, np.uint16)
        b1mask = int("FF00", 16)
        b1 = (uint16 & b1mask) >> (1 * 8)
        b2mask = int("00FF", 16)
        b2 = (uint16 & b2mask) >> (0 * 8)
        data_arr = bytearray([b1, b2, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        # val = int("%02X%02X" % (b1, b2), 16)    # should be equal to uint16
        # print("[uint16_to_bytearray] b1 = %mysched" % b1)
        # print("[uint16_to_bytearray] b2 = %mysched" % b2)
        # print("[uint16_to_bytearray] b1b2 = %d" % val)
        return data_arr

    @staticmethod
    def hexstr_to_uint16(hexstr):
        uint16 = int(hexstr, 16)
        uint16 = np.uint16(uint16)
        # print("[hexstr_to_uint16] hexstr = %mysched" % hexstr)
        # print("[hexstr_to_uint16] uint16 = %mysched" % uint16)
        return uint16

    @staticmethod
    def bytearray_to_hexstr(data_arr):
        isinstance(data_arr, bytearray)
        # cnt = 0
        hexstr = ""
        # for byte in msg.data:
        for byte in data_arr:
            # cnt = cnt + 1
            # print("byte %d = %mysched = %d = %02X" % (cnt, byte, byte, byte))
            hexstr_i = "%02X" % byte
            hexstr = hexstr + hexstr_i
        # print("[bytearray_to_hexstr] hexstr = %mysched" % hexstr)
        return hexstr

    @staticmethod
    def parse_recv_msg(msg, objctadd):
        if objctadd == 0x00:
            return ParseMsg.parse_esc_info(msg)
        if objctadd == 0x02:
            return ParseMsg.parse_voltage(msg)
        if objctadd == 0x03:
            return ParseMsg.parse_current(msg)
        if objctadd == 0x04:
            return ParseMsg.parse_rpm(msg)
        if objctadd == 0x05:
            return ParseMsg.parse_temperature(msg)
        if objctadd == 0x06:
            return ParseMsg.parse_inputthrottle(msg)
        if objctadd == 0x07:
            return ParseMsg.parse_outputthrottle(msg)
        if objctadd == 0x08:
            return ParseMsg.parse_mcuid(msg)
        if objctadd == 0x0B:
            return ParseMsg.parse_vcrtw(msg)
        if objctadd == 0x20:
            return ParseMsg.parse_turnoffesc(msg)
        if objctadd == 0x21:
            return ParseMsg.parse_restartesc(msg)
        if objctadd == 0x22:
            return ParseMsg.parse_warning(msg)

    @staticmethod
    def parse_arbitrid(arbitrid):
        priority_mask = int("FF000000", 16)
        sourceid_mask = int("00FF0000", 16)
        targetid_mask = int("0000FF00", 16)
        objctadd_mask = int("000000FF", 16)

        priority = (arbitrid & priority_mask) >> (3*8)
        sourceid = (arbitrid & sourceid_mask) >> (2*8)
        targetid = (arbitrid & targetid_mask) >> (1*8)
        objctadd = (arbitrid & objctadd_mask) >> (0*8)

        # print("[parse_arbitrid] priority = %mysched" % priority)
        # print("[parse_arbitrid] sourceid = %mysched" % sourceid)
        # print("[parse_arbitrid] targetid = %mysched" % targetid)
        # print("[parse_arbitrid] objctadd = %mysched" % objctadd)

        return [priority, sourceid, targetid, objctadd]

    @staticmethod
    def parse_esc_info(msg):
        if msg is None:
            return None
        return ParseMsg.bytearray_to_hexstr(msg.data)

    @staticmethod
    def parse_voltage(msg):
        if msg is None:
            return None
        hexstr = ParseMsg.bytearray_to_hexstr(msg.data)
        uint16 = ParseMsg.hexstr_to_uint16(hexstr)
        voltage = uint16 / 100
        return voltage

    @staticmethod
    def parse_current(msg):
        if msg is None:
            return None
        hexstr = ParseMsg.bytearray_to_hexstr(msg.data)
        uint16 = ParseMsg.hexstr_to_uint16(hexstr)
        current = uint16 / 100
        return current

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

    @staticmethod
    def parse_rpm(msg):
        if msg is None:
            return None
        hexstr = ParseMsg.bytearray_to_hexstr(msg.data)
        uint16 = ParseMsg.hexstr_to_uint16(hexstr)
        elec_rpm = float(uint16)
        num_mag_poles = 28    # KDE6213XF
        mech_rpm = elec_rpm * 60 * 2 / num_mag_poles
        return mech_rpm

    @staticmethod
    def parse_temperature(msg):
        if msg is None:
            return None
        hexstr = ParseMsg.bytearray_to_hexstr(msg.data)
        uint16 = ParseMsg.hexstr_to_uint16(hexstr)
        temp = float(uint16)    # / 100
        return temp

    @staticmethod
    def parse_inputthrottle(msg):
        if msg is None:
            return None
        hexstr = ParseMsg.bytearray_to_hexstr(msg.data)
        uint16 = ParseMsg.hexstr_to_uint16(hexstr)
        throttle = float(uint16)
        return throttle

    @staticmethod
    def parse_outputthrottle(msg):
        if msg is None:
            return None
        hexstr = ParseMsg.bytearray_to_hexstr(msg.data)
        uint16 = ParseMsg.hexstr_to_uint16(hexstr)
        throttle = float(uint16)    # / 100
        return throttle

    @staticmethod
    def parse_mcuid(msg):
        if msg is None:
            return None
        return ParseMsg.bytearray_to_hexstr(msg.data)

    @staticmethod
    def parse_warning(uint16):
        warning = "No warning"
        if uint16 & np.uint16(1) != 0:
            warning = "Stall Protection"
        elif uint16 & np.uint16(2) != 0:
            warning = "Over Temperature"
        elif uint16 & np.uint16(4) != 0:
            warning = "Overload Protection"
        elif uint16 & np.uint16(8) != 0:
            warning = "Low Voltage"
        elif uint16 & np.uint16(16) != 0:
            warning = "Over Voltage"
        elif uint16 & np.uint16(32) != 0:
            warning = "Voltage Cutoff( if enabled)"
        return warning

    @staticmethod
    def parse_vcrtw(msg):
        if msg is None:
            return None
        hexstr = ParseMsg.bytearray_to_hexstr(msg.data)

        uint16 = ParseMsg.hexstr_to_uint16(hexstr[0:4])
        voltage = float(uint16) / 100
        uint16 = ParseMsg.hexstr_to_uint16(hexstr[4:8])
        current = float(uint16) / 100
        uint16 = ParseMsg.hexstr_to_uint16(hexstr[8:12])
        rpm = float(uint16) * 60 * 2 / 28    # 28 poles in KDE6213XF
        uint16 = ParseMsg.hexstr_to_uint16(hexstr[12:14])
        temp = uint16
        uint16 = ParseMsg.hexstr_to_uint16(hexstr[14:16])
        warning = ParseMsg.parse_warning(uint16)

        vcrtw = [voltage, current, rpm, temp, warning]
        return vcrtw

    @staticmethod
    def parse_turnoffesc(msg):
        if msg is None:
            return None
        return ParseMsg.bytearray_to_hexstr(msg.data)

    @staticmethod
    def parse_restartesc(msg):
        if msg is None:
            return None
        return ParseMsg.bytearray_to_hexstr(msg.data)
