from ..modules.model.plotter import Plotter
from ..dispatchers.winddispatcher import WindDispatcher
from ..dispatchers.functiondispatcher import FunctionFromPoints
from ..utils.utils import remap

# position in paper, requires cropmark dection
# (in another version) to work dynamically
sketch_area_width = 4300
sketch_area_height = 4300
sketch_area_left_down = [1700, 5300]
sketch_area_right_down = [sketch_area_left_down[0] + sketch_area_width,
                          sketch_area_left_down[1]]
sketch_area_right_up = [sketch_area_right_down[0],
                        sketch_area_right_down[1] - sketch_area_height]
sketch_area_left_up = [sketch_area_left_down[0],
                       sketch_area_right_down[1] - sketch_area_height]
start_padding = 100


def check_if_inside_sketch_area(location):
    x, y = location
    if x > sketch_area_left_down[0] and x < sketch_area_right_down[0]:
        if y < sketch_area_left_down[1] and y > sketch_area_left_up[1]:
            return True


def intersects_boundary_at_y(location, boundary_x, radius):
    x, y = location
    if x > boundary_x - radius and x < boundary_x + round(radius / 2):
        return y
    else:
        return None


class WindtunnelDemo(object):
    """Documentation for Windtunnel

       How it works:
       The wind tunnel object accepts strokes within its canvas.
       On pen up a simulation will be ran
       (computes streamlines of wind passing through strokes)

       How to simulate:
       If the user crosses from outside the boundary to within,
       instead of adding more strokes to the canvas, it will fetch
       the according streamline and output it via muscle-plotter.

        How to test:
        Use muscle-plotter's anoto-mouse-emulator.py or
        a real-time OSC connection, e.g., via anoto.

    """

    def __init__(self):
        super(WindtunnelDemo, self).__init__()
        self.plotter = Plotter(self.handle_pendown,
                               self.handle_pendup,
                               self.handle_pendrag)
        self.windDispatcher = WindDispatcher(sketch_area_left_up[0],
                                             sketch_area_left_up[1],
                                             sketch_area_right_down[0],
                                             sketch_area_right_down[1])
        self.dispatcher = self.windDispatcher
        # records whether the pen was put
        # down inside the drawing area while dragging or not
        self.pen_down_was_inside_canvas = False
        self.fresh_streamline = True

    def find_streamline(self, location):
        print("plot: streamline")
        x, y = self.dispatcher.plot_streamline(
            remap(location[1], sketch_area_left_up[1],
            sketch_area_left_down[1], 200, 0))
        #print zip(x, y)
        points = zip([remap(xi, 0, 200, sketch_area_left_up[0],
                            sketch_area_right_up[0]) - location[0]
                      for xi in x],
                     [((yi - y[0]) / 200) * sketch_area_height / 2
                      for yi in y])
        #print points
        self.dispatcher = FunctionFromPoints(location[0],
                                             location[1],
                                             points)

    def handle_pendown(self, location):
        print("Pen down location {0}".format(location))
        if (intersects_boundary_at_y(location, sketch_area_left_up[0], 50) and
           self.fresh_streamline):
            self.fresh_streamline = False
            self.pen_down_was_inside_canvas = False
            self.find_streamline(location)
            self.dispatcher.serve(self.plotter, location)
        elif check_if_inside_sketch_area(location):
            self.dispatcher.serve(self.plotter, location)
            self.pen_down_was_inside_canvas = True

    def handle_pendrag(self, location):
        if (intersects_boundary_at_y(location, sketch_area_left_up[0], 50) and
           self.fresh_streamline):
            self.fresh_streamline = False
            self.pen_down_was_inside_canvas = False
            self.find_streamline(location)
            self.dispatcher.serve(self.plotter, location)
        elif (check_if_inside_sketch_area(location) and
              self.pen_down_was_inside_canvas):
            self.dispatcher.serve(self.plotter, location)

    def handle_pendup(self, location):
        print(location)
        if (check_if_inside_sketch_area(location) and
           self.pen_down_was_inside_canvas):
            self.dispatcher.runSimulation()
        self.plotter.deactivate()
        self.pen_down_was_inside_canvas = False
        self.fresh_streamline = True
        self.dispatcher = self.windDispatcher

    def end_application(self):
        self.plotter.end_plotter()
