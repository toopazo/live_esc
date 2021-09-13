#!/usr/bin/python3

import numpy as np
# import threading


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
        hexstr = ParseMsg.bytearray_to_hexstr(msg.data)
        escinfo = hexstr
        # escinfo = [int(x) for x in msg.data]

        return escinfo

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
        hexstr = ParseMsg.bytearray_to_hexstr(msg.data)

        mcuid = hexstr
        return mcuid

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
        hexstr = ParseMsg.bytearray_to_hexstr(msg.data)

        resp = hexstr
        return resp

    @staticmethod
    def parse_restartesc(msg):
        if msg is None:
            return None
        hexstr = ParseMsg.bytearray_to_hexstr(msg.data)

        resp = hexstr
        return resp
