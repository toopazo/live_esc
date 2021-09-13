import time
import serial
import signal
import sys


class ArduinoPWMClient:
    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        self.ser_timeout = 5
        self.ser = serial.Serial(
            port='/dev/ttyACM0',
            baudrate=115200,
            # parity=serial.PARITY_EVEN,
            # stopbits=serial.STOPBITS_ONE,
            # bytesize=serial.EIGHTBITS,
            timeout=self.ser_timeout   # read timeout
        )
        self.ser.isOpen()
        self.read_lines()   # check for initialization message

    def main(self):

        self.set_m1m2_throttle(1300, 1300)
        time.sleep(5)
        self.set_m1m2_throttle(900, 900)

        self.ser.close()

    def signal_handler(self, _signal, _frame):
        print('[signal_handler] calling self.bus.shutdown() ..')
        print(_signal)
        print(_frame)
        self.ser.close()
        sys.exit(0)

    def set_m1m2_throttle(self, v1, v2):
        cmd = 'm1v%sm2v%s' % (v1, v2)
        cmd = cmd.encode()
        self.ser.write(cmd)
        print("[set_m1m2_throttle] cmd %s " % cmd)

        self.read_lines()

    def read_lines(self):
        # print("[read_lines] Waiting for a message")

        # max_size = 50*100   # 50 lines of 100 characters
        # rline = self.ser.read(max_size)
        # print("[set_m1m2_throttle] size %s " % len(rline))
        # print(rline)

        t0 = time.time()
        titer = 0
        max_titer = 5
        # while True:
        while titer < max_titer:
            rline = self.ser.readline()
            print("[read_lines] rline %s " % rline)
            titer = time.time() - t0
            if '***'.encode() in rline:
                break
        telap = time.time() - t0
        print("[read_lines] telap %s " % telap)


if __name__ == '__main__':
    ardupwm = ArduinoPWMClient()
    ardupwm.main()
