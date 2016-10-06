from ..modules.model import canvas


BAR_WIDTH = 300


class NudgeAxis(object):
    """Defines a nudge axis
    """
    def __init__(self, origin, length, targets):
        super(NudgeAxis, self).__init__()
        self.origin = origin
        self.length = length
        self.targets = targets

    def serve(self, plotter, location):
        distance = canvas.calculate_distance(location, self.origin)
        if distance < 300:
            index_axis = canvas.SimpleFunction(0)
            index_axis.set_region(self.origin, 0,
                                  self.length, 600)
            index_axis.place_nudges_on_target(self.targets)
            index_axis.enable_pen_up()
            index_axis.disable_guide()
            index_axis.disable_boosts()
            plotter.place(index_axis)

    def check_if_inside(self, location):
        x, y = location
        low_x = self.origin[0] - 300
        high_x = self.origin[0] + self.length + 300
        if x > low_x and x < high_x:
            if y > self.origin[1] - 300 and y < self.origin[1] + 300:
                return True
