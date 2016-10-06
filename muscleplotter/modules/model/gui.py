""" Manages visualization of new reach model
"""
from PIL import Image, ImageDraw
import sys
if (sys.version_info < (3, 0)):
    import ConfigParser
    config = ConfigParser.ConfigParser()
else:
    import configparser
    config = configparser.ConfigParser()
config.read('configuration/defaults.cfg')

#static contigurations for reach model
INFO_AXIS_SHIFT = 2000
IMAGE_SIZE = (630, 850)


class GUI(object):

    image_index = 0

    def __init__(self):
        super(GUI, self).__init__()
        self.img = Image.new('RGB', IMAGE_SIZE, color=0)
        self.draw = ImageDraw.Draw(self.img)
        self.display_debug_image_at_end = config.getboolean('GUI','display_debug_image_at_end')
        # self._draw_circle((3000, 1000), 'red', 10)

    def refresh_img(self):
        self.img = Image.new('RGB', IMAGE_SIZE, color=0)
        self.draw = ImageDraw.Draw(self.img)

    def store_image(self, session_dir):
        # TODO: Maybe want to store one day.
        pass

    def _draw_circle(self, center, color, size):
        center = GUI.scale_point(center)
        x0 = center[0] - size
        x1 = center[0] + size
        y0 = center[1] - size
        y1 = center[1] + size
        self.draw.chord([x0, y0, x1, y1], 0, 360, color)

    def _draw_line(self, begin, end, color, weight):
        begin = GUI.scale_point(begin)
        end = GUI.scale_point(end)
        self.draw.line([begin, end], color, weight)

    def mark_pen_up(self, location):
        color = (255, 0, 0)
        self._draw_circle(location, color, 9)

    def mark_pen_down(self, location):
        color = (0, 255, 0)
        self._draw_circle(location, color, 7)

    def mark_pen_drag(self, location):
        color = (0, 125, 125)
        self._draw_circle(location, color, 3)

    def draw_targeting_nodes(self, decision_nodes):
        """
        Observed location connects to:
        Estimated location connects to:
        Optimal target
        """
        observed, estimated, target = decision_nodes
        self._draw_circle(observed, (10, 180, 120), 3)
        self._draw_line(observed, estimated, (20, 120, 255), 1)
        self._draw_circle(estimated, (0, 255, 0), 3)
        self._draw_line(estimated, target, (20, 120, 255), 1)
        self._draw_circle(target, (255, 0, 0), 3)

    def draw_brake_zone(self, location):
        location = self.shift_down(location)
        self._draw_circle(location, 4, (255, 255, 0), -1)

    def draw_observed_locations(self, points):
        color = (0, 200, 255)
        for point in points:
            self._draw_circle(self.shift_down(point), color, 1)

    def draw_cycles(self, location, slope_code=0):
        cycles = 120
        size = int(abs(slope_code))
        begin = self.shift_down(location, INFO_AXIS_SHIFT)
        if slope_code > 0:
            distance = INFO_AXIS_SHIFT + cycles + size * 40
            end = self.shift_down(location, distance)
        elif slope_code < 0:
            distance = INFO_AXIS_SHIFT - cycles - size * 40
            end = self.shift_down(location, distance)
        else:
            self._draw_circle(begin, (0, 255, 0), 3)
            return
        color = (20, (250 - size * 40), (110 + 30 * size))
        self._draw_line(begin, end, color, 1)

    def draw_decision_results(self, location, result, slope_code):
        color = (0, 230, 225)
        if not result:
            pass
        elif result == 'brake':
            color = (0, 0, 250)
            begin = self.shift_down(location, INFO_AXIS_SHIFT + 200)
            end = self.shift_down(location, INFO_AXIS_SHIFT - 200)
            self._draw_line(begin, end, color, 1)
            return
        elif result > 0:  # right
            self._draw_circle(self.shift_down(location, -500), color, 5)
        elif result < 0:  # left
            self._draw_circle(self.shift_down(location, 500), color, 5)
        self.draw_cycles(location, slope_code)

    def draw_targets(self, points):
        color = (255, 0, 0)
        for point in points:
            x, y = point
            self._draw_circle((x, y), color, 1)

    def draw_image(self):
        if self.display_debug_image_at_end:
            self.img.show()

    def shift_down(self, point, distance=False):
        x, y = point
        if not distance:
            point = (x, y + INFO_AXIS_SHIFT)
        else:
            point = (x, y + distance)
        return point

    @staticmethod
    def scale_point(point):
        x, y = point
        point = (int(x / 10), int(y / 10))
        return point
