from ..modules.model import canvas
from ..modules.windtunnel.windtunnelsimulator import WindSim
import numpy as np
from PIL import Image
from PIL import ImageOps
import time
from scipy.misc import imresize
import subprocess
import cv2
import os


class WindDispatcher(object):

    def __init__(self, start_x, start_y, end_x, end_y):
        super(WindDispatcher, self).__init__()
        self.active_area = (start_x, start_y, end_x, end_y)
        self.sketches = []
        self.simulation = None

    def serve(self, plotter, location):
        self.sketches.append(location)

    def calculate_height_index(self, y):
        """Determines the relative height of the starting point compared
        to tunnel height.

        Returns:
          (float): relative height from 0 - 1 where 0 bottom, 1 celling
        """
        h = float(self.active_area[3] - self.active_area[2])
        return (self.active_area[3] - y) / h

    def remap(self, x, oMin, oMax, nMin, nMax):
        # range check
        if oMin == oMax:
            return None
        if nMin == nMax:
            return None
        # check reversed input range
        reverseInput = False
        oldMin = min(oMin, oMax)
        oldMax = max(oMin, oMax)
        if not oldMin == oMin:
            reverseInput = True
        # check reversed output range
        reverseOutput = False
        newMin = min(nMin, nMax)
        newMax = max(nMin, nMax)
        if not newMin == nMin:
            reverseOutput = True
        portion = (x - oldMin) * (newMax - newMin) / (oldMax - oldMin)
        if reverseInput:
            portion = (oldMax - x) * (newMax - newMin) / (oldMax - oldMin)
        result = portion + newMin
        if reverseOutput:
            result = newMax - portion

        return result

    def plot_streamline(self, y):
        if self.simulation:
            line = self.simulation.get_streamline(y)
            return line

    def runSimulation(self):
        blur_size = 1
        gray_threshold = 240
        simulation_width = 200
        simulation_height = 200
        # color inverted because of openCV
        WHITE = 0  # 255,
        BLACK = 255  # 0
        # openCV parms
        DILATE_ITERATIONS = 5
        DILATE_MATRIX_SIZE = 20
        ERODE_ITERATIONS = 5
        SKIP_DILATE = False
        SKIP_CONTOURS = True
        SKIP_ERODE = False

        sketch_area_height = round(self.active_area[3] - self.active_area[1])
        sketch_area_width = round(self.active_area[2] - self.active_area[0])

        wind_area = np.empty(shape=(sketch_area_height, sketch_area_width),
                             dtype=np.uint8)
        wind_area[:] = WHITE
        print("size of image:" + str(wind_area.shape))
        print("sketches saved: " + str(len(self.sketches)))
        for point in self.sketches:
            # print("orig:"+str(point))
            y = self.remap(point[1], self.active_area[1],
                           self.active_area[3], 0, sketch_area_height - 1)
            x = self.remap(point[0], self.active_area[0],
                           self.active_area[2], 0, sketch_area_width - 1)
            # print("remaped: " + str([x,y]))
            for i in range(-blur_size, blur_size):
                for j in range(-blur_size, blur_size):
                    # print("saved and blurred "+ str(point))
                    wind_area[x + i, y + j] = BLACK

        # actually blur here just before the image conversion and rotation
        #(Image.fromarray(wind_area)).save("wind_pre.png")
        # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        kernel = np.ones((DILATE_MATRIX_SIZE, DILATE_MATRIX_SIZE), np.uint8)
        if not SKIP_DILATE:
            wind_area = cv2.dilate(wind_area, kernel,
                                   iterations=DILATE_ITERATIONS)

        # countours
        full_canvas_img = wind_area
        if not SKIP_CONTOURS:
            ret, thresh = cv2.threshold(wind_area, 127, 255, 0)
            _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE,
                                              cv2.CHAIN_APPROX_SIMPLE)
            #print("openCV/countours")
            #if isinstance(contours, list):
            #    print(len(contours))
            #    if (len(contours) > 0):
            #        print(len(contours[0]))
            full_canvas_img = cv2.drawContours(thresh, contours, -1,
                                               (128, 255, 0), 3)

        # erode those sketches
        if not SKIP_ERODE:
            full_canvas_img = cv2.erode(full_canvas_img, kernel,
                                        ERODE_ITERATIONS)

        # array to image & image manipulation
        full_canvas_img = Image.fromarray(full_canvas_img)
        full_canvas_img = full_canvas_img.rotate(90)
        # full_canvas_img = full_canvas_img.transpose(Image.FLIP_LEFT_RIGHT)
        # full_canvas_img = full_canvas_img.transpose(Image.FLIP_TOP_BOTTOM)
        # full_canvas_img = full_canvas_img.rotate(180)
        # full_canvas_img.save("full.png")
        # gaussian off for dilate
        # wind_area = gaussian_filter(wind_area, sigma=gaussian_power)
        # Image.fromarray(dilated).show()
        # full_canvas_blur_img = Image.fromarray(wind_area)
        # full_canvas_blur_img.save("blur.png")
        scaled_img = imresize(full_canvas_img, (simulation_width,
                                                simulation_height))

        for i in range(len(scaled_img)):
            for j in range(len(scaled_img[i])):
                if scaled_img[i][j] < gray_threshold:
                    # binarize again (blur and scales erode it)
                    scaled_img[i][j] = 0
        scaled_img = Image.fromarray(scaled_img)
        scaled_img = ImageOps.invert(scaled_img)

        self.simulation = WindSim(scaled_img)
        scaled_img.save(str(os.getcwd() +
                            "/muscleplotter/modules/windtunnel/data/load.png"))
