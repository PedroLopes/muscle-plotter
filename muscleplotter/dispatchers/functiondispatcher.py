from ..modules.model import canvas


class FunctionDispatcher(object):
    """Serves two functions for both cars

    """
    def __init__(self):
        super(FunctionDispatcher, self).__init__()

    def check_if_inside(self, location):
        x, y = location
        if x > self.origin[0] - 300 and x < self.origin[0] + 300:
            if y > self.origin[1] - 2300 and y < self.origin[1] + 2300:
                return True


class SegmentsFromPoints(FunctionDispatcher):
    """Linearly interpolate and connect points

    """
    def __init__(self, x, y, points):
        super(SegmentsFromPoints, self).__init__()
        self.origin = (x, y)
        self.points = points

    def serve(self, plotter, location):
        if not self.check_if_inside(location):
            return

        function_to_plot = canvas.ConnectAsSegments(self.points)
        function_to_plot.set_region(self.origin, 0, 4000, 3000)
        function_to_plot.enable_pen_up()
        plotter.place(function_to_plot)


class FunctionFromConstants(FunctionDispatcher):
    """Serves (i.e. displays) two functions from both cars

    """
    def __init__(self, x, y, constants, scaling=20):
        super(FunctionFromConstants, self).__init__()
        self.origin = (x, y)
        self.constants = constants
        self.scaling = scaling

    def serve(self, plotter, location):
        if not self.check_if_inside(location):
            return
        function_to_plot = canvas.SimpleFunction(self.scaling,
                                                 *self.constants)
        function_to_plot.set_region(self.origin, 0, 4000, 3000)
        function_to_plot.enable_pen_up()
        plotter.place(function_to_plot)


class FunctionFromPoints(FunctionDispatcher):
    """Interpolates given set of points

    """
    def __init__(self, x, y, points):
        super(FunctionFromPoints, self).__init__()
        self.origin = (x, y)
        self.points = points

    def serve(self, plotter, location):
        if not self.check_if_inside(location):
            return

        x_points, y_points = zip(*self.points)
        function_to_plot = canvas.ConnectPoints(self.points)
        function_to_plot.set_region(self.origin, 0, x_points[-1], 6000)
        function_to_plot.enable_pen_up()
        plotter.place(function_to_plot)
