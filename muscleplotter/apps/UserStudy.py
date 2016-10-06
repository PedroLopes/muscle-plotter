from __future__ import division, absolute_import
from __future__ import print_function, unicode_literals

from ..modules.model.plotter import Plotter
from ..dispatchers.UserStudyDispatcher import UserStudyDispatcher


class UserStudy(object):
    """Documentation for UserStudy
    Loads and serves user study functions as described in the paper.

    Attributes:
      studyFunctions (StudyFunctions()): controls target functions

      functionIndex (int): keeps track of number of trials

    """
    def __init__(self):
        super(UserStudy, self).__init__()
        self.plotter = Plotter(self.handle_pendown, self.handle_pendup)
        self.dispatcher = UserStudyDispatcher()
        self.functionIndex = 0
        self.next = True

        print('Wellcome to user study')
        while self.functionIndex < 16:
            if self.next:
                self.dispatcher.prepare_next_target()
                self.next = False
            print('Trial {0} is armed.'.format(self.functionIndex + 1))
            print("Press n to store and go to next one")
            print("Press r to clean and restart")
            print("Press q to break and leave")
            control = raw_input('make an entry')
            if control == 'n':
                self.functionIndex = self.functionIndex + 1
                self.next = True
            elif control == 'r':
                self.dispatcher.clean_and_restart()
            elif control == 'q':
                break

    def handle_pendown(self, location):
        print(location)
        self.dispatcher.serve(self.plotter, location)

    def handle_pendup(self, location):
        self.plotter.deactivate()

    def end_application(self):
        self.plotter.end_plotter()
