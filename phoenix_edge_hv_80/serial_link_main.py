import time
import serial
import sys


class CastleSerialLink:
    def __init__(self):
        self.serial = serial.Serial(
            '/dev/ttyUSB0', 19200, timeout=1
        )
        print(self.serial.name)  # check which port was really used

    def read_command(self):
        reply = self.serial.read()
        if len(reply) == 0:
            print('[read_command] Empty reply %s' % reply)
        else:
            print('[read_command] reply %s' % reply)
            # print('[read_command] reply %s' % bin(reply))
            # print('[read_command] reply %s' % format(reply, '08b'))

    def send_command(self, devid, regnum, regby1, regby2):
        self.serial.write(self.assemble_cmd(devid, regnum, regby1, regby2))

    def send_clrbuffcmd(self):
        self.serial.write(self.assemble_clrbuffcmd())

    def close_all(self):
        self.serial.close()  # close port

    def assemble_cmd(self, devid, regnum, regby1, regby2):
        # The first byte of the command contains a start bit and the device ID
        # of the Serial Link to communicate with.
        # Device ID’s can range from 0 to 63, allowing multiple Serial Links
        # on the same bus
        device_id_7bits = format(devid, '07b')
        # device_id_7bits = format(devid, '#07b')
        # device_id_7bits = format(devid, '#07b')
        # print('device_id_7bits %s' % device_id_7bits)
        byte0_str = str('1%s' % device_id_7bits)
        # print('[assemble_cmd] byte0_str %s' % byte0_str)
        # print('byte0_str.bit_length() %s ' % byte0_str.bit_length())
        # byte0_str = "%02X" % 0

        # The second byte specifies the register number;
        # note that there are separate addresses for reading and writing.
        # byte2 = "%02X" % 0
        byte1_str = format(regnum, '08b')
        # print('[assemble_cmd] byte1_str %s' % byte1_str)

        # The remaining bytes contain the data to write to the register,
        # the Command Data is ignored if it is a read address,
        # and a checksum to ensure that the transfer was not corrupted
        # byte2_str = "%02X" % 0
        # byte3_str = "%02X" % 0
        # byte4_str = "%02X" % 0
        byte2_str = format(regby1, '08b')
        byte3_str = format(regby2, '08b')
        # print('[assemble_cmd] byte2_str %s' % byte2_str)
        # print('[assemble_cmd] byte3_str %s' % byte3_str)
        sl_checksum = CastleSerialLink.compute_checksum(
            byte0_str, byte1_str, byte2_str, byte3_str)
        byte4_str = format(sl_checksum, '08b')
        # print('[assemble_cmd] byte4_str %s' % byte4_str)

        # verify checksum
        verif = CastleSerialLink.verify_checksum(
            byte0_str, byte1_str, byte2_str, byte3_str, byte4_str)
        if not verif:
            raise RuntimeError
        # print('[assemble_cmd] verif %s' % verif)

        # convert "barr" into an integer with base 16 (hexadecimal)
        barr = " ".join(
            [byte0_str, byte1_str, byte2_str, byte3_str, byte4_str])
        # print('barr |1 devid| regnum | regby1 | regby2 |')
        # print('[assemble_cmd] barr 7654321076543210765432107654321076543210')
        print('[assemble_cmd] barr %s' % barr)
        # barr = int(barr, 2)
        # print('[assemble_cmd] barr %s' % barr)
        # self.serial.write(barr)

        byte0 = int(byte0_str, 2)
        byte1 = int(byte1_str, 2)
        byte2 = int(byte2_str, 2)
        byte3 = int(byte3_str, 2)
        byte4 = int(byte4_str, 2)
        return bytearray([byte0, byte1, byte2, byte3, byte4])

    def assemble_clrbuffcmd(self):
        # At any time you can write a series of at least 5 0x00 bytes to
        # clear the command buffer. This is generally a good idea upon
        # initialization to ensure that the controller is in synch with the ESC.
        byte0_str = format(0, '08b')
        byte1_str = format(0, '08b')
        byte2_str = format(0, '08b')
        byte3_str = format(0, '08b')
        byte4_str = format(0, '08b')

        # sercmd = "".join(
        #     [byte0_str, byte1_str, byte2_str, byte3_str, byte4_str])
        # print('sercmd |1  devid| regnum | regby1 | regby2 |')
        # print('[assemble_clrbuffcmd] 7654321076543210765432107654321076543210')
        # print('[assemble_clrbuffcmd] %s' % sercmd)
        # sercmd = int(sercmd, 2)
        # print('[assemble_clrbuffcmd] %s' % sercmd)

        byte0 = int(byte0_str, 2)
        byte1 = int(byte1_str, 2)
        byte2 = int(byte2_str, 2)
        byte3 = int(byte3_str, 2)
        byte4 = int(byte4_str, 2)
        return bytearray([byte0, byte1, byte2, byte3, byte4])

    @staticmethod
    def compute_checksum(byte0, byte1, byte2, byte3):
        # The checksum is a modular sum. Correctly compute it as follows:
        # Checksum = 0 - (Byte 0 + Byte 1 + Byte 2 + Byte 3)
        # If the checksum is correct, the result of adding the bytes in the
        # command or response packet together will be 0x00 (ignoring overflows).
        # The response checksum can be verified by adding the Response Data
        # bytes and the response checksum, if valid they will total to
        # 0x00 (ignoring overflows).
        byte0 = int(byte0, 2)
        byte1 = int(byte1, 2)
        byte2 = int(byte2, 2)
        byte3 = int(byte3, 2)
        # checksum = 0 - (byte0 + byte1 + byte2 + byte3)
        checksum = byte0 + byte1 + byte2 + byte3
        # print('[compute_checksum] %s' % checksum)
        # print('[compute_checksum] %s' % bin(checksum))
        checksum_8bits = str(bin(checksum))
        checksum_8bits = " 0b%s" % checksum_8bits[-8:]
        # print('[compute_checksum] %s' % checksum_8bits)
        # checksum = (byte0 + byte1 + byte2 + byte3) % 255
        # print('[compute_checksum] %s' % checksum)
        # print('[compute_checksum] %s' % bin(checksum))
        return int(checksum_8bits, 2)

    @staticmethod
    def verify_checksum(byte0, byte1, byte2, byte3, byte4):
        byte0 = int(byte0, 2)
        byte1 = int(byte1, 2)
        byte2 = int(byte2, 2)
        byte3 = int(byte3, 2)
        byte4 = int(byte4, 2)

        sum_8bit = byte0 + byte1 + byte2 + byte3
        sum_8bit = str(bin(sum_8bit))
        sum_8bit = " 0b%s" % sum_8bit[-8:]
        sum_8bit = int(sum_8bit, 2)

        verify_checksum = sum_8bit - byte4
        # return verify_checksum

        if verify_checksum == 0:
            return True
        else:
            return False


if __name__ == '__main__':
    castle_link = CastleSerialLink()

    # ufilename = sys.argv[1]
    udevid = int(sys.argv[1])
    uregnum = int(sys.argv[2])
    uregby1 = int(sys.argv[3])
    uregby2 = int(sys.argv[4])

    # castle_link.assemble_cmd(udevid, uregnum, uregby1, uregby2)
    # castle_link.assemble_clrbuffcmd()
    for udevid in range(0, 64):
        print('testing udevid %s' % udevid)
        castle_link.send_clrbuffcmd()
        time.sleep(1)
        castle_link.send_command(udevid, uregnum, uregby1, uregby2)
        castle_link.read_command()
        time.sleep(1)
    castle_link.close_all()