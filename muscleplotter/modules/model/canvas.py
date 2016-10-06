"""Manages muscle plotter in specific canvas context

"""
from math import pi, sin, cos, radians, atan

import scipy.interpolate as ip
import numpy as np


def find_perpendicular(a):
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b


def calculate_segment_intersect(a1, a2, b1, b2):
    da = a2 - a1
    db = b2 - b1
    dp = a1 - b1
    dap = find_perpendicular(da)
    denom = np.dot(dap, db)
    num = np.dot(dap, dp)
    return (num / denom) * db + b1


def calculate_distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


class Canvas(object):
    """Manages instance related attributes of a plot on paper

    Attributes:
      active_area {'left': int, 'right': int,
                   'top': int, 'bottom': int}:
                   left right top bottom boundries
                   in anoto pixels where ems control is active.

      origin ((int),(int)): x and y
      major_axis_tilt (float): theta in degrees
      major_axis_span (int):
      minor_axis_span (int): amplitute x 2
    """
    def __init__(self):
        super(Canvas, self).__init__()
        self.plot_once = False
        self.no_guide = False
        self.no_boost = False
        self.nudge_on = False
        self.nudges = []

    def enable_pen_up(self):
        self.plot_once = True

    def disable_guide(self):
        self.no_guide = True

    def disable_boosts(self):
        self.no_boost = True

    def place_nudges_on_target(self, nudges):
        """Place locations to trigger nudges on paper

        Attributes:
          nudges ((int),(int)): set of points to activate a nudge
        """
        self.nudge_on = True
        self.nudges = dict(nudges)

    def set_region(self, origin, theta, major, minor):
        """Defines the canvas -active area- for the plot

        Attributes:
          origin ((int), (int)): x y on paper for the origin of the target
          theta (int): degrees of major axis shift. positive counter CW
          major (int): span of major axis.
          minor (int): span of minor axis. (Amplitude x 2)
        """
        self.origin = origin
        self.major_axis_tilt = theta
        self.major_axis_span = major
        self.minor_axis_span = minor

    def check_if_inside(self, location):
        """Used to check if observed point is in active ems region

        Given the origin and axis tilt, this method projects the
        observed location and checks whether it falls into
        the boundries defined by active region.

        Attributes:
          location ((int),(int)): (x, y) of observed anoto location

        Description:
          a1 ((float),(float)): origin
          a2: major axis end point
          b1: observed location as point
          b2: arbitary point that makes b perpendicular to major axis

        Returns:
          true (boolean): when anoto point is inside active region
          'done' (string): when observed location surpasses major axis
        """
        a1, a2 = self.calculate_major_axis_vectors()
        b1, b2 = self.calculate_minor_axis_vectors(location)
        # print a1, a2
        # print b1, b2
        intersect = calculate_segment_intersect(a1, a2, b1, b2)
        a1_to_intersect = (calculate_distance(intersect, a1))
        a2_to_intersect = (calculate_distance(intersect, a2))
        b1_to_intersect = (calculate_distance(intersect, b1))

        if (a1_to_intersect < self.major_axis_span and
           a2_to_intersect < self.major_axis_span):
            if b1_to_intersect < self.minor_axis_span / 2:
                return True
        elif (a1_to_intersect > self.major_axis_span and
              a2_to_intersect < self.major_axis_span):
            if b1_to_intersect < self.minor_axis_span:
                return 'done'

    def calculate_major_axis_vectors(self):
        """Defines two vectors that describe origin and end of major axis
        """
        v1 = np.array([self.origin[0], self.origin[1]])
        m = atan(radians(self.major_axis_tilt))
        v2_x = cos(m) * self.major_axis_span + self.origin[0]
        v2_y = -1 * sin(m) * self.major_axis_span + self.origin[1]
        return v1, np.array([v2_x, v2_y])

    def calculate_minor_axis_vectors(self, location):
        """Defines two vectors from observed location to an arbitary point
        that defines a perpendicular line segment to the major axis.
        """
        x, y = location
        v1 = np.array([x, y])
        denum = atan(radians(self.major_axis_tilt))
        if denum == 0:
            return v1, np.array([x, y + 1])
        m = - 1 / denum
        v2_x = cos(m) * x
        v2_y = -1 * sin(m) * y
        return v1, np.array([v2_x, v2_y])

    def revert_y_axis(self, coordinates):
        """Anoto y increases as you go down the paper.
        This method reverts calculated coordinates to map that

        Attributes:
          coordinates [((float),(float))]: array of points (x, y)
        """
        reverted_coordinates = []
        for point in coordinates:
            reverted_coordinates.append((point[0], -1 * point[1]))
        return reverted_coordinates

    def tilt_around_zero(self, coordinates):
        """Rotate target for the required orientation

        Attributes:
          coordinates [((float),(float))]: array of points (x, y)
        """
        theata = radians(self.major_axis_tilt)
        rm = np.array([[cos(theata), -sin(theata)],
                      [sin(theata), cos(theata)]], dtype='f')
        rotated_coordinates = []
        for point in coordinates:
            rotated_coordinates.append(np.dot(point, rm))
        return rotated_coordinates

    def shift_to_origin(self, coordinates):
        """Map calculated coordinates to the origin on the paper.

        Attributes:
          coordinates [((float),(float))]: array of points (x, y)
        """
        normalized_coordinates = []
        for point in coordinates:
            normalized_coordinates.append((self.origin[0] + point[0],
                                           self.origin[1] + point[1]))
        return normalized_coordinates

    def normalize_to_zero(self, y_coordinates):
        vertical_offset = y_coordinates[0]
        if vertical_offset == 0:
            return y_coordinates
        fix_offset = np.vectorize(lambda x: x - vertical_offset)
        y_coordinates = fix_offset(y_coordinates)
        return y_coordinates

    def prepare_coordinates(self, x_var, y_var):
        coordinates = zip(x_var, y_var)
        coordinates = self.revert_y_axis(coordinates)
        self.raw_coordinates = coordinates[:]
        coordinates = self.tilt_around_zero(coordinates)
        coordinates = self.shift_to_origin(coordinates)
        self.target_points = coordinates[::5]
        coordinates = zip(*coordinates)
        return coordinates


class SimpleFunction(Canvas):
    """Documentation for SimpleFunction

    """
    def __init__(self, scaling, *constants):
        super(SimpleFunction, self).__init__()
        self.constants = constants
        self.scaling = scaling

    def calculate_target_coordinates(self):

        def simple_function(x):
            y = 0
            x = float(x)
            for i, c in enumerate(reversed(self.constants)):
                y += c * (x / 2000) ** i
            return (y * self.scaling)

        calculate = np.vectorize(simple_function)
        x_variables = np.arange(self.major_axis_span, dtype=float)
        y_variables = calculate(x_variables)
        return self.prepare_coordinates(x_variables, y_variables)


class SimpleSine(Canvas):
    """Implements an extention for canvas, that desxcribes target coordinates.

    Attributes:
      period (int): period of the function (in anoto pixels)
      amplitude (int): amplitude (in anoto pixels)
      phase (int): phase offset (in degrees)
    """
    def __init__(self, period, amplitude, phase=0):
        super(SimpleSine, self).__init__()
        self.period = period
        self.amplitude = amplitude
        self.phase = phase

    def calculate_target_coordinates(self):

        amplitude = self.amplitude
        coef = (2 * pi) / self.period
        phase = radians(self.phase)

        def simple_sine(x):
            return (amplitude * sin((x * coef - phase)))
        calculate = np.vectorize(simple_sine)

        x_variables = np.arange(self.major_axis_span, dtype=float)
        y_variables = calculate(x_variables)
        y_variables = self.normalize_to_zero(y_variables)
        return self.prepare_coordinates(x_variables, y_variables)


class ConnectPoints(Canvas):
    """Generates a function that connects the given points

    Attributes:
      points [((int),(int))]: Array around origin 0,0 (in anoto units)
                              (x,y),...]

    """
    def __init__(self, points):
        super(ConnectPoints, self).__init__()
        self.points = points

    def calculate_target_coordinates(self):

        x_variables = np.arange(self.major_axis_span, dtype=int)
        xp = [p[0] for p in self.points]
        fp = [p[1] for p in self.points]
        fitline = ip.UnivariateSpline(xp, fp)
        return self.prepare_coordinates(x_variables, fitline(x_variables))


class ConnectAsSegments(Canvas):
    """Generates a function that connects given the points

    Attributes:
      points [((int),(int))]: Array around origin 0,0 (in anoto units)
                              (x,y),...]

    """
    def __init__(self, points):
        super(ConnectAsSegments, self).__init__()
        self.points = points

    def calculate_target_coordinates(self):

        x_variables = np.arange(self.major_axis_span, dtype=int)
        xp = [p[0] for p in self.points]
        fp = [p[1] for p in self.points]
        fitline = ip.interp1d(xp, fp, 'linear')
        return self.prepare_coordinates(x_variables, fitline(x_variables))
