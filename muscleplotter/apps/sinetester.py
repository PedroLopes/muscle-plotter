from ..modules.model.plotter import Plotter
from ..dispatchers.randomsinedispatcher import RandomSineDispatcher
from ..dispatchers.randomsinedispatcher import BasicSineDispatcher


class SineTester(object):
    """Documentation for Windtunnel

    """
    def __init__(self):
        super(SineTester, self).__init__()
        self.plotter = Plotter(self.handle_pendown, self.handle_pendup)
        selection = int(raw_input('(1) Random\n(2) Repeat'))
        if selection == 1:
            self.dispatcher = RandomSineDispatcher(280, 1000, 800, 7600)
        elif selection == 2:
            self.dispatcher = BasicSineDispatcher(280, 1000, 800, 7600)
        else:
            print 'Please input [1] or [2]'

    def handle_pendown(self, location):
        self.dispatcher.serve(self.plotter, location)

    def handle_pendup(self, location):
        self.plotter.deactivate()

    def end_application(self):
        self.plotter.end_plotter()
