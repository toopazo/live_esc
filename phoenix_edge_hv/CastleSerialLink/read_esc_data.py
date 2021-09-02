import time
import serial
from datetime import datetime
import pytz
import pickle
from  CastleSerialLinkControl import SerialLink, SerialLinkI2C


class EscSerialLink(SerialLink):
    def read_vars_in_range(self, rtuple):
        """
        Reads all values from the serial link register
        :return: the 3-byte response of the serial link for each register
        """
        if type(rtuple) is not tuple:
            raise RuntimeError('{} is not tuple'.format(rtuple))
        mdict = {}
        for key, val in self.register_dictionary.items():
            if rtuple[0] <= val <= rtuple[1]:
                result = self.read_var(key)
                mdict[key] = result
        return mdict


class EscData:
    """
    Class to read data from CastleSerialLinkControl.SerialLink(ser)
    """

    def __init__(self):
        self.data_dict = {}

    def append_data(self, mdict):
        for key, val in mdict.items():
            if key in self.data_dict:
                self.data_dict[key].append(val)
            else:
                self.data_dict[key] = [val]

    def save_to_file(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.data_dict, f, pickle.HIGHEST_PROTOCOL)

    def load_from_file(self, filename):
        with open(filename, 'rb') as f:
            self.data_dict = pickle.load(f)


def main_collect_data():
    # ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
    ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
    serlink_esc = EscSerialLink(ser)

    # Writing a 0[0x0000]to this register would be the same as the receiver
    # sending a 1.0ms pulse, OFF.  Writing 65535[0xFFFF]to this register
    # would be the same as the receiver sending a 2.0ms pulse, FULL THROTTLE.
    print(serlink_esc.write_var("write throttle", 10000))

    # print(pytz.all_timezones)
    # tz = pytz.timezone('Chile/Continental')
    tz = pytz.timezone('US/Eastern')
    tz_now = datetime.now(tz)
    print(tz)
    print(tz_now)

    nsamples = 100
    escdata = EscData()
    for i in range(0, nsamples):
        rdict = serlink_esc.read_vars_in_range((0, 5))
        rdict['time'] = str(datetime.now(tz))
        rdict['sample'] = i
        # print(rdict)
        escdata.append_data(rdict)

    print(serlink_esc.write_var("e stop", 1))
    time.sleep(2)
    print(serlink_esc.write_var("e stop", 0))
    time.sleep(2)

    print(serlink_esc.write_var("write throttle", 0))

    filename = 'esc_data.pkl'
    escdata.save_to_file(filename)
    escdata.data_dict = None
    escdata.load_from_file(filename)
    print(escdata.data_dict)


def main_read_data():
    filename = 'esc_data.pkl'
    escdata = EscData()
    escdata.load_from_file(filename)
    print(escdata.data_dict)


if __name__ == "__main__":
    # main_collect_data()
    # main_read_data()
    serlink_i2c = SerialLinkI2C('')
    serlink_i2c.simple_test_smbus()
    # serlink_i2c.simple_test_smbus2()

