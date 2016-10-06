from __future__ import print_function
from math import tan, radians, cos, sin, atan
import numpy as np
import sys

if (sys.version_info < (3, 0)):
    import ConfigParser
    config = ConfigParser.ConfigParser()
else:
    import configparser
    config = configparser.ConfigParser()
config.read('configuration/defaults.cfg')

# static configurations (tweak if needed)
MAIN_AXIS_SPEED_LIMIT = 2.5
MAIN_AXIS_SPEED_FLOOR = 0.05
MINOR_AXIS_SPEED_LIMIT = 3
NUDGE_ZONE = 60


def estimate_real_location(location, speed, delay):
    """Considering fix delay, extimate best slope to reach target
    """
    major_speed = limit_major_axis_speed(speed[0])
    minor_speed = limit_minor_axis_speed(speed[1])
    possible_x = location[0] + major_speed * delay * 1000
    possible_y = location[1] + minor_speed * delay * 1000
    return (possible_x, possible_y)


def limit_major_axis_speed(speed_value):
    if speed_value > MAIN_AXIS_SPEED_LIMIT:
        speed_value = MAIN_AXIS_SPEED_LIMIT
    elif speed_value < MAIN_AXIS_SPEED_FLOOR:
        speed_value = MAIN_AXIS_SPEED_FLOOR
    return speed_value


def limit_minor_axis_speed(speed_value):
    if abs(speed_value) > MINOR_AXIS_SPEED_LIMIT:
        if speed_value > 0:
            speed_value = MINOR_AXIS_SPEED_LIMIT
        if speed_value < 0:
            speed_value = -1 * MINOR_AXIS_SPEED_LIMIT
    return speed_value


class Target(object):
    """Generates and stores target coordinates. Serves reach model.
       Optionally: Receives the id to load pre-randomized functions.
    """

    def __init__(self, canvas):
        super(Target, self).__init__()

        self.fixed_delay = config.getfloat('Reach Control', 'fixed_delay')
        self.look_ahead = config.getfloat('Reach Control', 'look_ahead')
        self.to_mm = config.getfloat('Anoto Server', 'pixels_to_cm') / 10

        self.canvas = canvas
        self.origin = self.canvas.origin

        coordinates = self.canvas.calculate_target_coordinates()
        self.x_variables, self.y_variables = coordinates

    def rotate_and_transform_raw_coordinates(self, point):
        theata = radians(self.canvas.major_axis_tilt)
        rm = np.array([[cos(theata), -sin(theata)],
                      [sin(theata), cos(theata)]], dtype='f')
        rotated_point = np.dot(point, rm)
        return (rotated_point[0] + self.canvas.origin[0],
                rotated_point[1] + self.canvas.origin[1])

    def rotate_back_to_raw_for_index(self, point):
        point = (point[0] - self.canvas.origin[0],
                 point[1] - self.canvas.origin[1])
        theata = radians(-1 * self.canvas.major_axis_tilt)
        rm = np.array([[cos(theata), -sin(theata)],
                      [sin(theata), cos(theata)]], dtype='f')
        rotated_point = np.dot(point, rm)
        return int(rotated_point[0])

    def _get_next_target(self, location, estimate, speed):
        """Based on speed on main axis, return next plausable target

        if we aim to do 30 cycles at 250Hz: 0,12 seconds
        we should do 60 cycles to compansate fix delay: 0,24 seconds
        """
        check_for_region = self.canvas.check_if_inside(location)
        if not check_for_region:
            return None
        elif check_for_region == 'done':
            if self.canvas.plot_once:
                return check_for_region
            else:
                return None
        major_speed = limit_major_axis_speed(speed[0])
        minor_speed = limit_minor_axis_speed(speed[1])
        target_x = estimate[0] + (major_speed * self.look_ahead * 1000)
        target_y = estimate[1] + (minor_speed * self.look_ahead * 1000)
        y_index = self.rotate_back_to_raw_for_index((target_x, target_y))
        try:
            target = (y_index, self.canvas.raw_coordinates[y_index][1])
            target = self.rotate_and_transform_raw_coordinates(target)
            return target
        except:
            print ('No match for {} in targets array.'.format(y_index))
            return None

    def get_target_slope(self, location, speed):
        """ With the knowladge of speed and location, return desired slope
        """
        estimate = estimate_real_location(location, speed, self.fixed_delay)
        target = self._get_next_target(location, estimate, speed)
        if target is None or target == 'done':
            return target

        if self.canvas.nudge_on:
            for nudge in self.canvas.nudges:
                bar_ori = self.canvas.nudges[nudge]
                if bar_ori[0] < location[0]:
                    del self.canvas.nudges[nudge]
                    return 'nudge'

        if self.canvas.no_guide:
            return (estimate, target, 0)

        try:
            slope = (target[1] - estimate[1]) / (estimate[0] - target[0])
            # print('speed', speed)
            # print('location', location)
            # print('target', target)
            # print('calculated slope is', slope)
            angle = atan(slope)
            tilted_slope = tan(angle - radians(self.canvas.major_axis_tilt))
            return (estimate, target, tilted_slope)
        except:
            raise ValueError('Problem with slope calculation')
