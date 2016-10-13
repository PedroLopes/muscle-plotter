import random

from ..modules.model import canvas

major_span = 4300
minor_span = 3500
major_axis_tilt = 0
phase_offset = 90


class SineDispatcher(object):
    """Base class for sine dispatchers

    """
    def __init__(self, x1, x2, y1, y2):
        super(SineDispatcher, self).__init__()
        self.active_area = (x1, x2, y1, y2)

    def check_if_inside(self, location):
        x, y = location
        if x > self.active_area[0] and x < self.active_area[1]:
            if y > self.active_area[2] and y < self.active_area[3]:
                return True


class BasicSineDispatcher(SineDispatcher):
    """Documentation for BasicSineDispatcher

    """
    def __init__(self, x1, x2, y1, y2):
        super(BasicSineDispatcher, self).__init__(x1, x2, y1, y2)

    def serve(self, plotter, location):
        if not self.check_if_inside(location):
            return
        p = {'origin': location,
             'tilt': major_axis_tilt,
             'major': 4200,
             'minor': minor_span}
        p['period'] = 2800
        p['amplitude'] = -370
        p['phase'] = 0
        simple_sine = canvas.SimpleSine(p['period'],
                                        p['amplitude'],
                                        p['phase'])
        simple_sine.set_region(p['origin'], p['tilt'],
                               p['major'], p['minor'])
        # simple_sine.enable_pen_up()
        plotter.place(simple_sine)


class ParametricSineDispatcher(SineDispatcher):
    """Documentation for BasicSineDispatcher

    """
    def __init__(self, x1, x2, y1, y2, b=1):
        super(ParametricSineDispatcher, self).__init__(x1, x2, y1, y2)
        self.origin = ((x1 + x2) / 2, (y1 + y2) / 2)
        self.b = b

    def serve(self, plotter, location):
        if not self.check_if_inside(location):
            return
        p = {'origin': self.origin,
             'tilt': major_axis_tilt,
             'major': 4200,
             'minor': minor_span}
        p['period'] = 2800 / self.b
        p['amplitude'] = 370
        p['phase'] = 0
        simple_sine = canvas.SimpleSine(p['period'],
                                        p['amplitude'],
                                        p['phase'])
        simple_sine.set_region(p['origin'], p['tilt'],
                               p['major'], p['minor'])
        # simple_sine.enable_pen_up()
        plotter.place(simple_sine)


class RandomSineDispatcher(SineDispatcher):
    """Serves (i.e. displays) random sines onto the plotter based on pen down location

    Attributes:
      active_area ((int), (int), (int), (int)): to be hit for a streamline
                                          x-left, x-right, y-top, y-bottom
    """

    def __init__(self, x1, x2, y1, y2):
        super(RandomSineDispatcher, self).__init__(x1, x2, y1, y2)
        """divide active area into five to serve a diff line at each point
        """

    def serve(self, plotter, location):
        if not self.check_if_inside(location):
            return
        p = {'origin': location,
             'tilt': major_axis_tilt,
             'major': major_span,
             'minor': minor_span}
        p['period'] = random.randint(4000, 7000)
        p['amplitude'] = random.randint(200, 800)
        p['phase'] = random.randint(0, 90)
        random_sine = canvas.SimpleSine(p['period'],
                                        p['amplitude'],
                                        p['phase'])
        random_sine.set_region(p['origin'], p['tilt'],
                               p['major'], p['minor'])
        # random_sine.enable_pen_up()
        plotter.place(random_sine)
