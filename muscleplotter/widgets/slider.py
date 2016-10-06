from ..modules.model import canvas


class Slider(object):
    """Slider Widget for anoto paper and ems

    Attributes:
      origin ((int), (int)): x, y as anoto pixels
      length (int): length of slider in anoto pixels
      tilt (int): slider orientation in degrees. horizontal is zero
      value (float): 0 to 1 with respect to length
    """
    def __init__(self, origin, length, tilt, value):
        super(Slider, self).__init__()
        self.origin = origin
        self.length = length
        self.tilt = tilt
        self.value = value

    def serve(self, plotter, location):
        if not self.check_if_inside(location):
            return
        slider = canvas.SimpleFunction(0)
        slider.set_region(self.origin, self.tilt, self.map_value(), 1000)
        slider.enable_pen_up()
        slider.disable_guide()
        slider.disable_boosts()
        plotter.place(slider)

    def check_if_inside(self, location):
        x, y = location
        if x > self.origin[0] - 300 and x < self.origin[0] + 300:
            if y > self.origin[1] - 300 and y < self.origin[1] + 300:
                return True

    def map_value(self):
        return int(self.length * self.value)
