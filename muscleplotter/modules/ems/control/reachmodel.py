"""Implements new reach model to stay on the target
"""
# imports from python core and libraries
from __future__ import print_function
import time
from math import radians, cos, sin, atan
import sys

# imports from our system
from reachstats import ReachStats
from pulse import Pulse
from target import Target

if (sys.version_info < (3, 0)):
        import ConfigParser
        config = ConfigParser.ConfigParser()
else:
        import configparser
        config = configparser.ConfigParser()
config.read('configuration/defaults.cfg')

# static definitions for brake strategy (tweak if you need)
MIN_BRAKE_CYCLES = 11
MAX_BRAKE_CYCLES = 44
SPEED_MIN = 0
SPEED_MAX = 3

def remap_speed_to_brake(value):
    """Maps speed to number of brake cycles required
    """
    left_min = SPEED_MIN
    left_max = SPEED_MAX
    right_min = MIN_BRAKE_CYCLES
    right_max = MAX_BRAKE_CYCLES
    left_span = left_max - left_min
    right_span = right_max - right_min
    value_scaled = float(value - left_min) / float(left_span)
    return int(right_min + (value_scaled * right_span))


class ReachModel(object):
    """Reach model instructs left and right pulse objects.

    Pulse objects are orchestrated according to the new reach model.
    """
    def __init__(self, ems, gui):
        super(ReachModel, self).__init__()

        self.verbose = config.getboolean('Reach Control', 'console_stats')
        self.brake_channel = config.get("Extra EMS Channels","brake_active")

        self.ems = ems
        self.gui = gui
        self.left = Pulse(1)
        self.right = Pulse(2)
        self.penup = Pulse(3)
        self.brake = Pulse(4)

        self.last_index = 0

        self.brake_zone = config.getint('Reach Control', 'brake_zone')
        self.fixed_delay = config.getfloat('Reach Control', 'fixed_delay')
        pulse_period = config.getfloat('EMS Machine', 'ems_period')
        self.reach_repetitions = int(self.fixed_delay / pulse_period)

        self.CONTROL_ON = False
        self.BRAKE_MODE = False
        """Establishes state transfer from execute_repetions
        """
        self.stats = ReachStats()

    def create_target(self, canvas):
        self.target = Target(canvas)
        self.gui.draw_targets(canvas.target_points)

    def get_ready_for_next_one(self):
        self.last_index = 0
        self.stats = ReachStats()

    def start_control(self):
        """Waits for the suitable time to start the control strategies.
        """
        self.CONTROL_ON = True
        while self.CONTROL_ON:
            plot_state = self._control_repetions()
            if plot_state == 'done':
                print('PLOT: ended')
                for i in range(50):
                    self.ems.pulsate(self.penup)
                print('ACTION: Pen Up')
                break
            elif (plot_state == 'no sample' or
                  plot_state == 'no target' or
                  plot_state == 'nudged'):
                time.sleep(self.fixed_delay / 2)

    def end_control(self):
        self.CONTROL_ON = False

    def restart_plot(self):
        self.end_control()
        time.sleep(self.fixed_delay * 2)
        self.last_index = 0
        self.stats = ReachStats(self.config)
        self.result.refresh_for_next()

    def terminate_control(self):
        self.end_control()
        time.sleep(self.fixed_delay * 2)
        self.stats.pause_timer()
        duration = self.stats.total_time
        print('PLOT: Duration {0:5.1f} seconds.'.format(duration))
        # save to file: duration
        self.stats.print_timing_analysis()
        self.ems.print_timing_analysis()

    def handle_penup(self):
        self.left.end_boost()
        self.right.end_boost()
        self.stats.reset_for_pen_up()

    def project_speed_to_tilted_axis(self, speed):
        if speed[0] == 0:
            return (0, 0)
        speed_vector_theata = atan(speed[1] / speed[0])
        speed_vector_amp = ((speed[0] ** 2) + (speed[1] ** 2)) ** 0.5
        axis_tilt = radians(-1 * self.target.canvas.major_axis_tilt)
        tilted_vector_theata = speed_vector_theata - axis_tilt
        projected_x = cos(tilted_vector_theata) * speed_vector_amp
        projected_y = sin(tilted_vector_theata) * speed_vector_amp
        return (projected_x, projected_y)

    def _control_repetions(self):
        """Using speed and location calculate target and distance.

        Determine required reach repetions based on parameters and
        execute accordingly.
        """
        if not self.ems.EMS_ON:
            return 'no sample'
        current_stats = self.stats.get_last()
        if not current_stats:
            return 'no sample'
        location, speed = current_stats
        tilted_speed = self.project_speed_to_tilted_axis(speed)
        target_params = self.target.get_target_slope(location, speed)
        if target_params == 'done':
            return 'done'
        elif target_params == 'nudge':
            self._execute_nudge()
            return 'nudged'
        elif target_params:
            self.stats.star_timer()
            estimate, target, target_slope = target_params
        else:
            return 'no target'
        if len(self.stats.decisions) == 0:
            target_slope = 0
        if len(self.stats.decisions) == 1:
            if abs(target_slope) > 0.3:
                if target_slope > 0:
                    target_slope = 0.3
                elif target_slope < 0:
                    target_slope = -0.3
        slope_code = self.left.target_slope(target_slope)
        slope_code = self.right.target_slope(target_slope)
        self.stats.register_decision(location, estimate, target)
        nodes = self.stats.get_targeting()
        self.gui.draw_targeting_nodes(nodes)
        result = self.stats.analyze_distance_to_target()
        brake_repetions = 0

        if not result:
            pass
        elif self.BRAKE_MODE:
            result = 'brake'
            self.left.end_boost()
            self.right.end_boost()
            brake_repetions = remap_speed_to_brake(abs(tilted_speed[1]))
            self.left.apply_brake()
            self.right.apply_brake()
        elif result > 0:
            if not self.target.canvas.no_boost:
                self.right.boost_amp()
                self.left.end_boost()
        elif result < 0:
            if not self.target.canvas.no_boost:
                self.left.boost_amp()
                self.right.end_boost()
        else:
            self.left.end_boost()
            self.right.end_boost()

        # index for decisions to anoto events
        index = len(self.stats.events)
        samples_between = index - self.last_index
        self.last_index = index

        if self.verbose:
                print(' {0:3d}#'.format(len(self.stats.decisions)), end='')
                print('  Slope: {0:6.1f}'.format(target_slope), end='')
                indicator = str(int(1000 * 10 ** -slope_code)).zfill(7)
                print('  |{0:3}|  '.format(indicator), end='')
                print('L: {0:2} '.format(self.left.boost_indicator()), end='')
                print('R: {0:2} '.format(self.right.boost_indicator()), end='')
                print(' Brake: {0:2}'.format(brake_repetions), end='')
                print('   Anoto: {0:2d}'.format(samples_between))

        if result == 'brake':
            self._execute_repetions(brake_repetions, mode='brake')
        else:
            self._execute_repetions(self.reach_repetitions, mode='travel')

    def _execute_repetions(self, cycles, mode):
        """Pulsates and observes current way to the target.
        """
        for cycle in range(cycles):
            if not self.ems.EMS_ON:
                return
            if not mode == 'brake' or not self.brake_channel:
                self.ems.pulsate(self.left, self.right)
            elif self.brake_channel:
                self.ems.pulsate(self.brake)
            distances = self.stats.get_distance_to_target()
            if distances:
                distance, _, _ = distances
            if mode == 'brake':
                last_speed = self.stats.speed[-1]
                tilted_speed = self.project_speed_to_tilted_axis(last_speed)
                if (abs(tilted_speed[1]) < 0.1 and
                   not cycles == self.reach_repetitions):
                    print('BRAKE: ended')
                    self.BRAKE_MODE = False
                    return
            elif mode == 'travel':
                if self.stats.check_target_crossing():
                    self.BRAKE_MODE = True
                    print('TRAVEL: ended')
                    return
        if self.BRAKE_MODE:
            self.BRAKE_MODE = False

    def _execute_nudge(self):
        repeat = 9
        print('NUDGE: nudging')
        self.left.target_slope(20)
        for i in range(repeat):
            self.ems.pulsate(self.left)
        self.right.target_slope(20)
        for i in range(repeat):
            self.ems.pulsate(self.right)
