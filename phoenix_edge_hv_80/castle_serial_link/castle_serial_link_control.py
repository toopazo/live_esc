import numpy as np
from smbus2 import SMBus, i2c_msg
# from smbus import SMBus
import wiringpi


class SerialLink:
    """
    Class to communicate with castle serial link, takes Pyserial Serial class
    in constructor
    """

    def __init__(self, serial, device_id=0):
        """
        :param serial: Pyserial Serial class
        :param device_id: number between 0-63 associate with serial link address

        """

        assert isinstance(device_id, int)
        assert 0 <= device_id < 64

        # assign class
        # default baudrate is 9600 and device id is 0 on the serial link
        self.serial_link = serial

        self.device_id = device_id

        # Addresses for registers, taken from serial link manual
        self.register_dictionary = {
            "voltage": 0, "ripple": 1, "current": 2, "throttle": 3, "power": 4,
            "speed": 5, "temp": 6, "BEC voltage": 7, "BEC current": 8,
            "Raw NTC": 9, "RAW linear": 10, "link live": 25, "fail safe": 26,
            "e stop": 27, "packet in": 28, "packet out": 29, "check bad": 30,
            "packet bad": 31, "write throttle": 128, "write fail safe": 129,
            "write e stop": 130, "write packet in": 131,
            "write packet out": 132, "write check bad": 133,
            "write packet bad": 134
        }

        # Scales for converting from bytes to integers,
        # taken from serial link manual. -1 means do not scale
        self.scale_dictionary = {
            "voltage": 20.0, "ripple": 4.0, "current": 50.0, "throttle": 1.0,
            "power": 0.2502, "speed": 20416.66, "temp": 30.0,
            "BEC voltage": 4.0, "BEC current": 4.0, "Raw NTC": 63.8125,
            "RAW linear": 30.0, "link live": -1, "fail safe": -1, "e stop": -1,
            "packet in": -1, "packet out": -1, "check bad": -1, "packet bad": -1
        }

    def calc_checksum(self, rsp):
        """
        Verify the incoming checksum from the serial link
        :param rsp: a byte array, has shape (3,). The first two values are read,
         and the -1 value is the checksum
        :return: True if checksum is valid, false if not
        """

        intlist = [int(a) for a in rsp]

        # Calculate the checksum
        if np.sum(intlist) % 256 == 0:
            return True
        else:
            return False

    def append_checksum(self, array):
        """
        array is list of size 4. Appends the checksum of the first 4 bytes to
        the end of the list
        :param array: a list of size 4, contains the command we are writing the
        the serial link
        :return: array with  the checksum
        """

        array.append((0 - np.sum(array)) % 256)
        return array

    def convert_response(self, var, rsp):
        """
        :param var: The variable we requested, e.g. "voltage"
        :param rsp: the 3-byte response of the serial link. The last byte is a
        checksum
        :return: The converted response
        """

        # extract the values from the byte array
        values = rsp[:2]

        # get the the scale to multiply the values by
        scale = self.scale_dictionary[var]

        # if scale = -1, there is no scale associated with it in the manual
        if scale == -1:
            return values[0] * 256 + values[1]
        else:
            return (values[0] * 256 + values[1]) * scale / 2042.0

    def write_var(self, var, s):
        """
        Sends a command to the serial link
        :param var: the register to write to, e.g. "speed"
        :param s: integer between 0 and 65535 to write to the register
        :return: the response of the serial link, which is just confirmation of
        the command we sent
        with a checksum appended. This does not contain new information
        """
        assert 0 <= s < 256**2
        assert isinstance(s, int)

        # the list of bytes (as integers) to write to the serial link
        # byte 1 is the device address, always starts with 1xxxxxxx hence a 128
        # byte 2 is the register address
        # bytes 3-4 are the values to be written to the register
        # byte 5 is a checksum
        write_array = [128 + self.device_id,
                     self.register_dictionary[var],
                     int(s // 256), s % 256]

        write_array = self.append_checksum(write_array)

        self.serial_link.write(write_array)

        # 3 byte response from serial link confirming command was sent
        rsp = self.serial_link.read(3)
        return rsp

    def read_var(self, var):
        """
        Reads a value from the serial link register
        :param var: the register to read from, e.g. "speed"
        :return: the 3-byte response of the serial link
        """

        # byte 1 is the device address, always starts with 1xxxxxxx hence a 128
        # byte 2 is the register address
        # bytes 3-4 are ignored by the serial link since we are reading
        # byte 5 is a checksum
        read_array = [128 + self.device_id,
                      self.register_dictionary[var],
                      0, 0]
        read_array = self.append_checksum(read_array)

        self.serial_link.write(read_array)
        rsp = self.serial_link.read(3)

        # check that the response is indeed 3 bytes and the checksum is correct
        if len(rsp) == 3 and self.calc_checksum(rsp):
            return self.convert_response(var, rsp)
        else:
            arg = "Invalid response from serial link. " \
                  "The response was: {}".format(rsp)
            raise Exception(arg)


class SerialLinkI2C(SerialLink):
    def simple_test_wiringpi(self):
        bus = SMBus(1)
        # 7 bit address (will be left shifted to add the read write bit)
        address = 0x0b
        reg_read_voltage = self.register_dictionary['voltage']
        reg_write_throttle = self.register_dictionary['write throttle']

        #          76543210
        # add = int('00001011', 2)  # address 11
        # add = int('00010110', 2)  # address 11 + write bit
        # add = int('00010111', 2)  # address 11 + read bit
        # add = int('00001100', 2)  # address 12

        # var = 'voltage'
        var = 'write throttle'
        reg = self.register_dictionary[var]
        wlen = 5
        rlen = 3

        # b = bus.read_byte_data(i2c_addr=80, register=0)
        # print(b)

        # byte 1 is the 7bit device address
        # byte 2 is the register address
        # bytes 3-4 are ignored by the serial link since we are reading
        # byte 5 is a checksum

        # 10000 = 00100111 00010000
        b1 = int('00100111', 2)
        b0 = int('00010000', 2)

        # Write an array of registers
        data = [b1, b0]
        data = self.append_checksum(data)
        data = list(data)
        print('data %s' % data)
        bus.write_i2c_block_data(address, reg_write_throttle, data)
        # block = bus.read_i2c_block_data(address, reg_write_throttle, rlen)
        block = bus.read_byte(address)
        print('block %s' % block)
        block = bus.read_byte(address)
        print('block %s' % block)
        block = bus.read_byte(address)
        print('block %s' % block)

        bus.close()

    def simple_test_smbus(self):
        bus = SMBus(1)
        # 7 bit address (will be left shifted to add the read write bit)
        address = 0x0b
        reg_read_voltage = self.register_dictionary['voltage']
        reg_write_throttle = self.register_dictionary['write throttle']

        #          76543210
        # add = int('00001011', 2)  # address 11
        # add = int('00010110', 2)  # address 11 + write bit
        # add = int('00010111', 2)  # address 11 + read bit
        # add = int('00001100', 2)  # address 12

        # var = 'voltage'
        var = 'write throttle'
        reg = self.register_dictionary[var]
        wlen = 5
        rlen = 3

        # b = bus.read_byte_data(i2c_addr=80, register=0)
        # print(b)

        # byte 1 is the 7bit device address
        # byte 2 is the register address
        # bytes 3-4 are ignored by the serial link since we are reading
        # byte 5 is a checksum

        # 10000 = 00100111 00010000
        b1 = int('00100111', 2)
        b0 = int('00010000', 2)

        # Write an array of registers
        data = [b1, b0]
        data = self.append_checksum(data)
        data = list(data)
        print('data %s' % data)
        bus.write_i2c_block_data(address, reg_write_throttle, data)
        # block = bus.read_i2c_block_data(address, reg_write_throttle, rlen)
        block = bus.read_byte(address)
        print('block %s' % block)
        block = bus.read_byte(address)
        print('block %s' % block)
        block = bus.read_byte(address)
        print('block %s' % block)

        bus.close()

    def simple_test_smbus2(self):
        # Open i2c bus 1 and read one byte from address 80, offset 0
        bus = SMBus(1)
        # bus.open(1)
        add = int('0b', 16)
        # var = 'voltage'
        var = 'write throttle'
        reg = self.register_dictionary[var]
        wlen = 5
        rlen = 3

        # b = bus.read_byte_data(i2c_addr=80, register=0)
        # print(b)

        # byte 1 is the 7bit device address
        # byte 2 is the register address
        # bytes 3-4 are ignored by the serial link since we are reading
        # byte 5 is a checksum
        b1 = int('00100111', 2)    # d10000 = 00100111 00010000 = d39 d16
        b0 = int('00010000', 2)
        read_array = [add,
                      self.register_dictionary[var],
                      b1, b0]
        read_array = self.append_checksum(read_array)

        # # Write a block of 8 bytes to address 80 from offset 0
        data = [b0, b1]
        bus.write_i2c_block_data(i2c_addr=add, register=reg, data=data)
        print('data %s' % data)

        # Read a block of 3 bytes from address 80, offset 0
        # block = bus.read_i2c_block_data(i2c_addr=add, register=reg, length=3)
        # Returned value is a list of 16 bytes
        # print('block %s' % block)

        msg = i2c_msg.read(address=add, length=rlen)
        bus.i2c_rdwr(msg)
        # block = msg.data.contents.block[1:rlen + 1]
        for value in msg:
            print(value)
        # msg.data.contents.block[1:length + 1]

        bus.close()
