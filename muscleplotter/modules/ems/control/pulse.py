"""Stores and manages a channel for the EMS device.

Handles mode transitions with required initilizations
Examples:
  left = Pulse(1, 10)
  left.set_duty_range(50, 210)
"""
import sys
if (sys.version_info < (3, 0)):
        import ConfigParser
else:
        import configparser
from ballisticpairs import BallisticPairs

MAX_AMP = 15
MAX_DUTY = 499
config = ConfigParser.ConfigParser()
config.read('configuration/defaults.cfg')


class Pulse(object):
    """An object to store and manupulate pulse variables
    Based on the mode of the pulse, duty_cycle is modified.
    Properties:
      mode (int): selected mode for the instance
      current_duty (int):stores current duty value
    Args:
      channel (int): determines the channel on ems machine
      amp (int): amplitude of the pulse
    """

    def __init__(self, channel):
        super(Pulse, self).__init__()

        self.channel = channel
        self.current_duty = 0

        user = config.get('User', 'name')
        self.pairs = BallisticPairs(user)
        self.amp = self.pairs.get_amp(self.channel)
        if self.channel == 3 or self.channel == 4:
            self.start_at_duty(self.pairs.get_duty(self.channel))

        self.boost_mode = False
        self.boost_mode_max = False
        self.brake_mode = False

    def start_at_duty(self, duty):
        """Sets current duty cycle. Can be used reinitlize duty cycle value
        Args:
          duty (int): desired duty_cycle in range
        """
        self.current_duty = duty

    def boost_amp(self):
        if self.boost_mode:
            if self.boost_mode_max:
                pass
            else:
                self.amp += 1
                # print ('Channel {0:d} is boosted to {1:d}'
                #    .format(self.channel, self.amp))
                self.boost_mode_max = True
        else:
            self.amp += 1
            # print ('Channel {0:d} is boosted to {1:d}'
            #        .format(self.channel, self.amp))
            self.boost_mode = True

    def end_boost(self):
        if self.boost_mode_max:
            self.amp -= 2
            self.boost_mode_max = False
            self.boost_mode = False
            # print ('Channel {0:d}s max boost ends, back to {1:d} amps'
            #        .format(self.channel, self.amp))
        elif self.boost_mode:
            self.amp -= 1
            # print ('Channel {0:d}s boost ends, back to {1:d} amps'
            #        .format(self.channel, self.amp))
            self.boost_mode = False
        else:
            pass

    def boost_indicator(self):
        if self.boost_mode:
            if self.boost_mode_max:
                return '11'
            else:
                return '1'
        else:
            return ''

    def brake_indicator(self):
        if self.brake_mode:
            return 'B'
        else:
            return ''

    def generate_pulse(self):
        """Used to extract variables
        Raises:
          ValueError if duty value is more then max.
        Returns:
          (channel (int), duty_cycle (int), amplitude(int))
        """
        if self.current_duty > MAX_DUTY:
            raise ValueError('This duty value is too high', self.current_duty)
        if self.amp > MAX_AMP:
            raise ValueError('This amp value is too high', self.current_duty)
        return (self.channel, self.current_duty, self.amp)

    def target_slope(self, slope):
        self.brake_mode = False
        code, pair = self.pairs.get_pair(slope)
        self.start_at_duty(pair[self.channel - 1])
        return code

    def apply_brake(self):
        self.brake_mode = True
        code, pair = self.pairs.get_pair('b')
        self.start_at_duty(pair[self.channel - 1])
