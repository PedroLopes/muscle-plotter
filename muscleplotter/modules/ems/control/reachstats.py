from __future__ import print_function
import time
import numpy as np
import sys
if (sys.version_info < (3, 0)):
    import ConfigParser
    config = ConfigParser.ConfigParser()
else:
    import configparser
    config = configparser.ConfigParser()

config.read('configuration/defaults.cfg')


# TODO: compile with static variables !!
def calculate_distance(observed, target):
    x1, y1 = observed
    x2, y2 = target
    horizontal_distance = abs(x2 - x1)
    vertical_distance = (y2 - y1)
    distance = (horizontal_distance**2 + vertical_distance**2) ** 0.5
    return (distance, horizontal_distance, vertical_distance)


class Decision(object):
    """Documentation for Decision

    """
    def __init__(self, observed, estimated, target):
        super(Decision, self).__init__()
        self.observed = observed
        self.estimated = estimated
        self.target = target

    def get_items(self):
        return (self.observed, self.estimated, self.target)


class ReachStats(object):
    """Belongs to ReachModel, stores data for the current run.

    Attributes:
      decisions [((point),(point),(point))]: Array of decision points
                observed location, estimated location, optimum target
      distances [float]:
      observed_locations [(point)]: anoto coordinates log
    """

    def __init__(self):
        super(ReachStats, self).__init__()

        self.pixels_to_cm = config.getfloat('Anoto Server', 'pixels_to_cm')
        self.lag_cycles = config.getint('Reach Control', 'cycles_till_boost')
        self.brake_zone = config.getint('Reach Control', 'brake_zone')
        self.boost_threshold = config.getint('Reach Control', 'boost_thresh')

        self.coordinates = []
        self.events = []
        self.speed = []
        self.decisions = []
        self.distances = []
        self.y_distances = []
        self.lag_log = []

        self.anoto_timing = []
        self.total_time = 0
        self.timer = 0

    def get_distance_to_target(self):
        if len(self.coordinates) == 0:
            return False
        observed = self.coordinates[-1]
        target = self.decisions[-1].target
        distance = calculate_distance(observed, target)
        self.y_distances.append(distance[2])
        self.distances.append(distance[0])
        return distance

    def reset_for_pen_up(self):
        # reset lag effects
        self.y_distances = []
        self.lag_log = []
        self.coordinates = []

    def check_target_crossing(self):
        """Analyses y distance and difference to spot zero crossing
        """
        if len(self.y_distances) > 0:
            latest_y_distance = self.y_distances[-1]
        if len(self.lag_log) > 0:
            if abs(self.lag_log[-1]) > 100:
                difference = latest_y_distance - self.lag_log[-1]
                if latest_y_distance > 0:
                    if latest_y_distance + difference < self.brake_zone:
                        return 'brake'
                elif latest_y_distance < 0:
                    if latest_y_distance + difference > -1 * self.brake_zone:
                        return 'brake'

    def analyze_distance_to_target(self):
        if len(self.y_distances) > 0:
            average_y = np.average(self.y_distances)
        else:
            return
        self.y_distances = []
        self.lag_log.append(average_y)
        if len(self.lag_log) > self.lag_cycles * 2:
            test_region = self.lag_log[-self.lag_cycles:]
            sum_lag = sum(test_region)
            if sum_lag < 0:
                if (abs(sum_lag) >
                   self.lag_cycles * self.boost_threshold):
                    return 1
            if sum_lag > 0:
                if (abs(sum_lag) >
                   self.lag_cycles * self.boost_threshold):
                    return -1
        return 0

    def feed_anoto_time(self, measured_time):
        self.anoto_timing.append(measured_time)

    def print_timing_analysis(self):
        border = 10
        if len(self.anoto_timing) < 2 * border:
            return False
        analyze_window = len(self.anoto_timing) - border
        stamps = self.anoto_timing[border:analyze_window]
        deltas = []
        for i in range(len(stamps) - 1, 2, -1):
            deltas.append(stamps[i] - stamps[i - 1])
        print ('Total of this many anoto events: {}'
               .format(len(self.anoto_timing)))
        print ('Number of all deltas {}'.format(len(deltas)))
        deltas = [d for d in deltas if d > 0.009]
        print ('Number of filtered deltas {}'.format(len(deltas)))

        # filter out pen ups
        deltas = [d for d in deltas if d < 0.5]
        freq = 1 / np.average(deltas)
        print ('Anoto sample frequency was: {0:.2f} Hz'
               .format(freq))
        print ('StdDev of delays is {0:.3f} seconds'
               .format(np.std(deltas)))
        self.anoto_timing = []

    def star_timer(self):
        if self.total_time == 0 and self.timer == 0:
            print('TIMER: started')
            self.timer = time.time()

    def resume_timer(self):
        if self.total_time > 0:
            self.timer = time.time()

    def pause_timer(self):
        if self.timer != 0:
            self.total_time += time.time() - self.timer
        self.timer = 0

    def register_decision(self, observed, estimated, target):
        targeting_nodes = Decision(observed, estimated, target)
        self.decisions.append(targeting_nodes)

    def feed_data(self, speed, event):
        self.events.append(event)
        location = (event[0], event[1])
        self.coordinates.append(location)
        self.speed.append(speed)

    def get_targeting(self):
        return self.decisions[-1].get_items()

    def get_last(self):
        try:
            return (self.coordinates[-1], self.speed[-1])
        except:
            return None

    def print_distances_to_target(self):
        average_distance = np.average(self.distances) / self.pixels_to_cm
        std_dev = np.std(self.distances) / self.pixels_to_cm
        print ('Average distance was {0:.3f}cm'.format(average_distance))
        print ('Distance StdDev is {0:.3f}'.format(std_dev))
