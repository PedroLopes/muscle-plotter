from ..modules.model import canvas


BAR_WIDTH = 300


class BarChart(object):
    """Defines a bar chart for given values using muscle plotter

    Assumes that axes are defined on paper.
    Maps bar to the main axis, activates required one on pen down.

    Attributes:
      origin ((int), (int)): x, y as anoto pixels
      length (int): length of bar chart in anoto pixels
      height (int): defines bar chart height in pixels
      values {(int):(float)}: a dict of values for each bar, from 0 to 1
    """
    def __init__(self, origin, length, height, values):
        super(BarChart, self).__init__()
        self.origin = origin
        self.length = length
        self.height = height
        self.values = values

        self.index_served = False
        self.bar_origins = {}
        self.get_bar_origins()

    def serve(self, plotter, location):
        if not self.index_served:
            distance = canvas.calculate_distance(location, self.origin)
            if distance < 300:
                index_axis = canvas.SimpleFunction(0)
                index_axis.set_region(self.origin, 0,
                                      self.length, 600)
                index_axis.place_nudges_on_target(self.bar_origins)
                index_axis.enable_pen_up()
                index_axis.disable_guide()
                index_axis.disable_boosts()
                plotter.place(index_axis)
        else:
            if not self.check_if_inside(location):
                return
            bar_index = self.map_to_bar_index(location)
            # print bar_index
            if not bar_index:
                return
            bar = canvas.SimpleFunction(0)
            bar.set_region(self.bar_origins[bar_index], 90,
                           self.map_value(bar_index), 5000)
            bar.enable_pen_up()
            bar.disable_guide()
            bar.disable_boosts()
            plotter.place(bar)

    def check_if_inside(self, location):
        x, y = location
        low_x = self.origin[0] - 300
        high_x = self.origin[0] + self.length + 300
        if x > low_x and x < high_x:
            if y > self.origin[1] - 300 and y < self.origin[1] + 300:
                return True

    def get_bar_origins(self):
        each_bar = self.length / (len(self.values) + 1)
        for value in self.values:
            x_location = self.origin[0] + (value * each_bar)
            self.bar_origins[value] = (x_location, self.origin[1])

    def map_to_bar_index(self, location):
        # print self.bar_origins
        for i in self.bar_origins:
            if abs(self.bar_origins[i][0] - location[0]) < BAR_WIDTH:
                return i

    def map_value(self, bar_index):
        return int(self.height * self.values[bar_index])
