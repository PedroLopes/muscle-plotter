from __future__ import division, absolute_import
from __future__ import print_function, unicode_literals

from ..modules.model import canvas

import random
import ConfigParser
import json
import os
from math import sin, pi


class UserStudyDispatcher(object):
    """Maps each trial to a target functions of the user study
    """

    def __init__(self):
        super(UserStudyDispatcher, self).__init__()
        self.targetFunctionList = range(0, 8) * 2
        random.shuffle(self.targetFunctionList)
        print(self.targetFunctionList)
        self.functionIndex = -1

        config = ConfigParser.ConfigParser()
        config.read("./configuration/defaults.cfg")
        self.functionFile = config.get("User Study Functions", "function_file")
        self.pen_up_active = config.get("Extra EMS Channels","up_active")
        # TODO: should be looking to config file
        self.vertical_span = 5000
        self.major_axis = 3900
        self.origin = (1100, 6000)

        params = ConfigParser.ConfigParser()
        target = "./configuration/user_study/" + self.functionFile
        params.read("./configuration/user_study/" + self.functionFile)
        self.f = {}
        self.f['period'] = json.loads(params.get("sinewaves", "period"))
        self.f['amplitude'] = json.loads(params.get("sinewaves", "amplitude"))
        self.f['a'] = json.loads(params.get("sinewaves", "a"))
        self.f['b'] = json.loads(params.get("sinewaves", "b"))
        self.f['c'] = json.loads(params.get("sinewaves", "c"))
        self.f['d'] = json.loads(params.get("sinewaves", "d"))
        self.f['phase_offset1'] = json.loads(
            params.get("sinewaves", "phase_offset1"))
        self.f['phase_offset2'] = json.loads(
            params.get("sinewaves", "phase_offset2"))
        self.f['feature_width'] = json.loads(
            params.get("features", "feature_width"))
        print(self.f)

    def check_if_inside(self, location):
        x, y = location
        if x > self.origin[0] - 500 and x < self.origin[0] + 400:
            if y > self.origin[1] - 2300 and y < self.origin[1] + 2300:
                return True

    def _prepare_math_broken_funcion(self):
        self.points = []
        period = self.f['period'][2]
        amplitude = self.f['amplitude'][2]
        a = self.f['a'][2]
        b = self.f['b'][2]
        c = self.f['c'][2]
        d = self.f['d'][2]
        phase_offset1 = self.f['phase_offset1'][2]
        phase_offset2 = self.f['phase_offset2'][2]
        coef = (2 * pi) / period
        self.inside = False
        self.freeze = -9999
        tolerance = 0.3

        def math_broken_func(x):
            fundamental = amplitude * sin(x * coef)
            if b == 0:
                superimposed_1 = 0
            else:
                superimposed_1 = (amplitude * a *
                                  sin((x * coef / b) + phase_offset1))
            if c == 0:
                superimposed_2 = 0
            else:
                superimposed_2 = (amplitude * c *
                                  sin((x * coef / d) + phase_offset2))

            if (self.freeze - tolerance <=
               (fundamental + superimposed_1 + superimposed_2) <=
               self.freeze + tolerance):
                self.inside = False
            elif x != 0 and (x % int(period / 2)) == 0:
                if not self.inside:
                    self.inside = True
                    self.freeze = (fundamental +
                                   superimposed_1 + superimposed_2)
            if self.inside:
                return self.freeze
            return (fundamental + superimposed_1 + superimposed_2)

        for index in range(self.major_axis):
            point = (index, math_broken_func(index))
            self.points.append(point)

    def _prepare_math_valley_funcion(self):
        print('saw theet')
        self.points = []
        half_period = 1000
        valley_period = 2 * half_period

        def math_valley_func(x):
            if (x % valley_period) < half_period:
                return (x % valley_period)
            else:
                return valley_period - (x % valley_period)

        for index in range(self.major_axis):
            point = (index, math_valley_func(index))
            self.points.append(point)

    def _prepare_math_function(self):
        self.points = []
        period = self.f['period'][self.targetFunctionID]
        amplitude = self.f['amplitude'][self.targetFunctionID]
        a = self.f['a'][self.targetFunctionID]
        b = self.f['b'][self.targetFunctionID]
        c = self.f['c'][self.targetFunctionID]
        d = self.f['d'][self.targetFunctionID]
        phase_offset1 = self.f['phase_offset1'][self.targetFunctionID]
        phase_offset2 = self.f['phase_offset2'][self.targetFunctionID]
        coef = (2 * pi) / period

        def math_func(x):
            fundamental = amplitude * sin(x * coef)
            if b == 0:
                superimposed_1 = 0
            else:
                superimposed_1 = (amplitude * a *
                                  sin((x * coef / b) +
                                      phase_offset1))
            if c == 0:
                superimposed_2 = 0
            else:
                superimposed_2 = (amplitude * c *
                                  sin((x * coef / d) +
                                      phase_offset2))
            return fundamental + superimposed_1 + superimposed_2

        for index in range(self.major_axis):
            point = (index, math_func(index))
            self.points.append(point)

    def _normalize_points(self, points):
        bias = points[0][1]
        print('bias', bias)
        return [(p[0], p[1] - bias) for p in points]

    def prepare_next_target(self):
        self.functionIndex = self.functionIndex + 1
        self.targetFunctionID = self.targetFunctionList[self.functionIndex]
        print(self.targetFunctionID)
        if self.f['period'][self.targetFunctionID] == -1:
            print('broken')
            self._prepare_math_broken_funcion()
        elif self.f['period'][self.targetFunctionID] == -2:
            print('saw theet')
            self._prepare_math_valley_funcion()
        else:
            print('sinewave')
            self._prepare_math_function()

    def clean_and_restart(self):
        pass

    def serve(self, plotter, location):
        if not self.check_if_inside(location):
            print("not inside")
            return
        function_to_plot = canvas.ConnectAsSegments(
            self._normalize_points(self.points))
        function_to_plot.set_region(self.origin, 0,
                                    self.major_axis,
                                    self.vertical_span)
        if (self.pen_up_active):
            function_to_plot.enable_pen_up()
        plotter.place(function_to_plot)
