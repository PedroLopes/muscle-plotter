#python imports
from __future__ import print_function
import threading
import time
import numpy as np
import sys

#imports from our system
from interface.SerialThingy import SerialThingy
import interface.singlepulse as singlepulse

if (sys.version_info < (3, 0)):
    import ConfigParser
    config = ConfigParser.ConfigParser()
else:
    import configparser
    config = configparser.ConfigParser()
config.read('configuration/defaults.cfg')

DEBUG = False

class EMS(object):
    """Provides and controls bare minimum ems connection
    """
    def __init__(self):
        super(EMS, self).__init__()

        self.control_actuation = True
        self.EMS_ON = False
        self.timing_analysis = []
        self.ems_period = config.getfloat('EMS Machine', 'ems_period')

        self.connect_ems()

    def connect_ems(self):

        SERIAL_RESPONSE = False
        fake = config.getboolean('EMS Machine', 'fake_connection')
        self.ems = SerialThingy(fake)
        if not fake:
            address = config.get('EMS Machine', 'machine_address')
            self.ems.open_port(address, SERIAL_RESPONSE)
        else:
            self.ems.open_port(None, SERIAL_RESPONSE)

    def start_control_thread(self, function):

        self.c_thread = threading.Thread(target=function, args=())
        self.c_thread.start()

    def stop_actuation(self):

        self.control_actuation = False
        self.c_thread.join()

    def set_ems_on(self):
        self.EMS_ON = True

    def turn_ems_off(self):
        self.EMS_ON = False

    def _send_single_pulse(self, chan, duty, amp, delay=0):

        if self.EMS_ON:
            self.ems.write(singlepulse.generate(chan, duty, amp))
            if delay == 0:
                pass
            elif delay == 1:
                time.sleep(self.ems_period)
            elif delay == 0.5:
                time.sleep(self.ems_period / 2)

    def pulsate(self, *pulses):

        if self.EMS_ON:
            for pulse in pulses:
                    chan, duty, amp = pulse.generate_pulse()
                    self.ems.write(singlepulse.generate(chan, duty, amp))
                    time.sleep(self.ems_period / len(pulses))
                    self.timing_analysis.append(time.time())

    def print_timing_analysis(self):
        border = 20
        if len(self.timing_analysis) < 2 * border:
            return False
        analyis_lenght = len(self.timing_analysis) - border
        print('Total of {} pulse pairs has been sent'
              .format(analyis_lenght))
        stamps = self.timing_analysis[border:analyis_lenght]
        deltas = []
        for i in range(len(stamps) - 1, 2, -1):
            deltas.append(stamps[i] - stamps[i - 1])
        # print('Filter out pen ups')
        deltas = [d for d in deltas if d < 0.1]
        print ('For {} pulses:'.format(analyis_lenght))
        freq = 1 / np.average(deltas)
        print ('Pulse frequency was: {0:.2f} Hz'
               .format(freq))
        print ('StdDev of sleep times: {0:.6f} seconds'
               .format(np.std(deltas)))
        self.timing_analysis = []
