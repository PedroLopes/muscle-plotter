import serial
import SerialThread


class SerialThingy(object):
        def __init__(self, fake, writeFakeToConsole=False):
                self.ser = None
                # i'm wondering if this should have a default, which is False
                self.fake = fake
                # defaulted to false
                self.writeFakeToConsole = writeFakeToConsole

        def sendFakeWritesToConsoleOutput(self, value):
                self.writeFakeToConsole = value

        def open_port(self, port, listening_serial_thread):
                if not self.fake:
                        self.ser = serial.Serial(port,
                                                 baudrate=115200,
                                                 bytesize=serial.EIGHTBITS,
                                                 parity=serial.PARITY_NONE,
                                                 stopbits=serial.STOPBITS_TWO,
                                                 #rtscts=True,
                                                 timeout=1000)
                if listening_serial_thread:
                    SerialThread.SerialThread(self.ser).start()

        def write(self, msg):
                if not self.fake:
                        self.ser.write(msg)
                elif self.writeFakeToConsole:
                        # writes the EMS serial message to the console / stdout
                        print(msg)
