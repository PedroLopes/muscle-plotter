"""An interface to create reach model instances on anoto paper.

Establishes EMS and Anoto Connections on initialize.
Accepts canvas objects to execute muscle plots.

"""
import time
from threading import Thread

from ..anoto.anotoconnect import Anoto
from ..ems.emsconnect import EMS
from gui import GUI
from ..ems.control.reachmodel import ReachModel


class Plotter(object):
    """Manages reach model instances

    """
    canvas_index = 1

    def __init__(self,
                 pen_down_action=None,
                 pen_up_action=None,
                 pen_drag_action=None):
        super(Plotter, self).__init__()

        if not pen_down_action:
            def pen_down_action(location):
                return
        if not pen_up_action:
            def pen_up_action(location):
                return
        if not pen_drag_action:
            def pen_drag_action(location):
                return

        self.anoto = Anoto()
        self.ems = EMS()
        self.gui = GUI()
        self.model = ReachModel(self.ems, self.gui)
        self.active_models = []

        def anoto_callback(addr, tags, pen_data, source):
            speed = self.anoto.speed.get_vector()
            self.model.stats.feed_data(speed, pen_data)
            self.model.stats.feed_anoto_time(time.time())
            if pen_data[2] == "down":
                self.ems.EMS_ON = True
                self.model.stats.resume_timer()
                location = (pen_data[0], pen_data[1])
                self.gui.mark_pen_down(location)
                pen_down_action(location)
                # print('Anoto: Pen Down')
            elif pen_data[2] == "up":
                self.ems.EMS_ON = False
                self.model.stats.pause_timer()
                self.model.handle_penup()
                self.anoto.speed.reset_measure()
                location = (pen_data[0], pen_data[1])
                self.gui.mark_pen_up(location)
                pen_up_action(location)
                # print('Anoto: Pen Up')
            elif pen_data[2] == "drag":
                location = (pen_data[0], pen_data[1])
                self.gui.mark_pen_drag(location)
                pen_drag_action(location)
                # print('Anoto: Pen Drag')

        self.anoto.set_callback_function(anoto_callback)
        self.anoto.start_osc_server()

    def place(self, canvas):
        self.model.create_target(canvas)
        t = Thread(target=lambda: self.model.start_control())
        t.start()
        t.setName('control_loop_' + str(Plotter.canvas_index))
        print(str(t.getName()) + ' has been created')
        Plotter.canvas_index += 1
        self.active_models.append(t)

    def deactivate(self):
        if self.model.CONTROL_ON:
            self.model.terminate_control()
            t = self.active_models.pop()
            t.join()
            self.model.get_ready_for_next_one()
            print(str(t.getName()) + ' has been terminated')

    def end_plotter(self):
        self.gui.draw_image()
        self.anoto.close_connection()
