from time import clock
import matplotlib.animation as anim
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import scipy.misc
from sys import argv
import os


class WindSim(object):
    """Documentation for WindSimulation

    """
    # np.set_printoptions(threshold=np.nan)
    plot_active = True if len(argv) == 1 else False
    #turn on all debug prints
    DEBUG = True
    #load images as RGB rather than B/W
    RGB_MODE = False
    #save all animation frames
    save = True
    #save a streamlot from matplotlib
    PLOT_STREAMLINES = True
    #save animation frames as a movie (mp4)
    SAVE_MOVIE = True
    #save individual streamlines from user's position
    PLOT_INDIVIDUAL_STREAMLINES = True
    #plots streamlines at regular intervales
    PLOT_CUSTOM_STREAMLINES = True
    #steps
    step_range = 20

    # lattice height
    height = 200  
    # lattice width
    width = 200
    # fluid viscosity
    viscosity = 0.02  
    # "relaxation" parameter
    omega = 1 / (3 * viscosity + 0.5)  
    # initial and in-flow speed
    u0 = 0.1  
    # abbreviations for lattice-Boltzmann weight factors
    four9ths = 4.0 / 9.0
    one9th = 1.0 / 9.0
    one36th = 1.0 / 36.0
    # set to True if performance data is desired
    performanceData = True

    # Initialize all the arrays to steady rightward flow:
    # particle densities along 9 directions
    n0 = four9ths * (np.ones((height, width)) - 1.5 * u0**2)
    nN = one9th * (np.ones((height, width)) - 1.5 * u0**2)
    nS = one9th * (np.ones((height, width)) - 1.5 * u0**2)
    nE = one9th * (np.ones((height, width)) +
                   3 * u0 + 4.5 * u0**2 - 1.5 * u0**2)
    nW = one9th * (np.ones((height, width)) -
                   3 * u0 + 4.5 * u0**2 - 1.5 * u0**2)
    nNE = one36th * (np.ones((height, width)) +
                     3 * u0 + 4.5 * u0**2 - 1.5 * u0**2)
    nSE = one36th * (np.ones((height, width)) +
                     3 * u0 + 4.5 * u0**2 - 1.5 * u0**2)
    nNW = one36th * (np.ones((height, width)) -
                     3 * u0 + 4.5 * u0**2 - 1.5 * u0**2)
    nSW = one36th * (np.ones((height, width)) -
                     3 * u0 + 4.5 * u0**2 - 1.5 * u0**2)
    # macroscopic density
    rho = (n0 + nN + nS +
           nE + nW + nNE +
           nSE + nNW + nSW)
    # macroscopic x velocity
    ux = (nE + nNE + nSE -
          nW - nNW - nSW) / rho
    # macroscopic y velocity
    uy = (nN + nNE + nNW -
          nS - nSE - nSW) / rho

    # Initialize barriers:
    barrier = np.zeros((height, width), bool)
    full_path = os.getcwd() + "/muscleplotter/modules/windtunnel/"

    def __init__(self, image=None):
        super(WindSim, self).__init__()

        if image:
            (width, height) = image.size
            imageData = np.array(image)

            x = 0
            y = 0
            for y in range(height):
                for x in range(width):
                    if imageData[x][y] == 0:
                        WindSim.barrier[x, y] = True
                    else:
                        WindSim.barrier[x, y] = False
                    x += 1
                y += 1

        else:

            # load the WindSim.barrier as an image file
            if WindSim.RGB_MODE:
                loaded_img = self.rgb2gray(mpimg.imread(
                    WindSim.full_path + "data/" + 'load.png', bool))
            else:
                loaded_img = mpimg.imread(
                    WindSim.full_path + "data/" + 'load.png', bool)

            barrier_img = loaded_img
            # the img is png so i gotta go pixel per pixel
            # and invert the colors to True/False
            if WindSim.DEBUG:
                print(barrier_img)
                print("img" + str(len(barrier_img)))

            x = 0
            y = 0
            for y in range(WindSim.height):
                for x in range(WindSim.width):
                    if barrier_img[y, x] == 0:
                        WindSim.barrier[y, x] = True
                    else:
                        WindSim.barrier[y, x] = False
                    x += 1
                y += 1

        # scipy.misc.imsave('barierImage.png', WindSim.barrier)

        if WindSim.DEBUG:
            print("WindSim.barrier definitions")
            print("raw_len:" + str(len(WindSim.barrier)))
            print("WindSim.width:" + str(WindSim.width))
            print("WindSim.height:" + str(WindSim.height))
            print("col_l:" + str(len(WindSim.barrier) / WindSim.height))
            print(WindSim.barrier)

        # sites just north of barriers
        self.barrierN = np.roll(WindSim.barrier, 1, axis=0)
        # sites just south of barriers
        self.barrierS = np.roll(WindSim.barrier, -1, axis=0)
        # etc.
        self.barrierE = np.roll(WindSim.barrier, 1, axis=1)
        self.barrierW = np.roll(WindSim.barrier, -1, axis=1)
        self.barrierNE = np.roll(self.barrierN, 1, axis=1)
        self.barrierNW = np.roll(self.barrierN, -1, axis=1)
        self.barrierSE = np.roll(self.barrierS, 1, axis=1)
        self.barrierSW = np.roll(self.barrierS, -1, axis=1)

        # Here comes the graphics and animation...
        theFig = plt.figure(figsize=(20, 10))  # 8,3
        self.fluidImage = plt.imshow(self.curl(WindSim.ux, WindSim.uy),
                                     origin='lower',
                                     norm=plt.Normalize(-.1, .1),
                                     cmap=plt.get_cmap('jet'),
                                     interpolation='none')
        # an RGBA image
        bImageArray = np.zeros((WindSim.height, WindSim.width, 4), np.uint8)
        # set alpha=255 only at WindSim.barrier sites
        bImageArray[WindSim.barrier, 3] = 255
        self.barrierImage = plt.imshow(bImageArray, origin='lower',
                                       interpolation='none')

        # Function called for each successive animation frame:
        self.startTime = clock()
        if (WindSim.save):
            self.frameList = open('output/frameList.txt', 'w')
            # file containing list of images (to make movie)
            self.frame_c = 0

        animation = anim.FuncAnimation(theFig, self.nextFrame,
                                       interval=0.1, frames=self.step_range, blit=False)
        animation.new_saved_frame_seq()
        if self.SAVE_MOVIE:
            Writer = anim.writers['ffmpeg']
            writer = Writer(fps=15, metadata=dict(artist='muscle-plotter'), bitrate=1800)
            animation.save('output/realtime_simulation.mp4', writer=writer)

        if WindSim.plot_active:
            pass

        plt.figure()

        # plot the streamlines
        if self.PLOT_STREAMLINES:
            x_1 = np.linspace(-1, 1, len(WindSim.ux))
            y_1 = np.linspace(-1, 1, len(WindSim.uy))
            plt.streamplot(x_1, y_1, WindSim.ux, WindSim.uy, density=1, color='b')
            plt.savefig('output/streamplot.png')

        # plot the streamline follower at regular intervals
        if self.PLOT_CUSTOM_STREAMLINES:
            xRange = range(0, 200)
            yRange = range(0, 200)
            plt.clf()
            for y_start_value in range(5, 196, 5):
                x, y = self.follow_through(WindSim.ux, WindSim.uy, y_start_value)
                plt.plot(x, y)
            plt.plot(xRange, yRange)
            plt.savefig('output/custom_streamlines.png')

    def rgb2gray(self, rgb):
        r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray

    # Move all particles by one step along their directions of motion (pbc):
    def stream(self):
        # pedro: this basically shifts the array by one step at a time,
        # we could parametrize "1" as step to go "faster"
        # axis 0 is north-south; + direction is north
        WindSim.nN = np.roll(WindSim.nN, 1, axis=0)
        WindSim.nNE = np.roll(WindSim.nNE, 1, axis=0)
        WindSim.nNW = np.roll(WindSim.nNW, 1, axis=0)
        WindSim.nS = np.roll(WindSim.nS, -1, axis=0)
        WindSim.nSE = np.roll(WindSim.nSE, -1, axis=0)
        WindSim.nSW = np.roll(WindSim.nSW, -1, axis=0)
        # axis 1 is east-west; + direction is east
        WindSim.nE = np.roll(WindSim.nE, 1, axis=1)
        WindSim.nNE = np.roll(WindSim.nNE, 1, axis=1)
        WindSim.nSE = np.roll(WindSim.nSE, 1, axis=1)
        WindSim.nW = np.roll(WindSim.nW, -1, axis=1)
        WindSim.nNW = np.roll(WindSim.nNW, -1, axis=1)
        WindSim.nSW = np.roll(WindSim.nSW, -1, axis=1)
        # Use tricky boolean arrays to handle
        # WindSim.barrier collisions (bounce-back):
        WindSim.nN[self.barrierN] = WindSim.nS[WindSim.barrier]
        WindSim.nS[self.barrierS] = WindSim.nN[WindSim.barrier]
        WindSim.nE[self.barrierE] = WindSim.nW[WindSim.barrier]
        WindSim.nW[self.barrierW] = WindSim.nE[WindSim.barrier]
        WindSim.nNE[self.barrierNE] = WindSim.nSW[WindSim.barrier]
        WindSim.nNW[self.barrierNW] = WindSim.nSE[WindSim.barrier]
        WindSim.nSE[self.barrierSE] = WindSim.nNW[WindSim.barrier]
        WindSim.nSW[self.barrierSW] = WindSim.nNE[WindSim.barrier]

    # Collide particles within each cell to redistribute velocities
    # (could be optimized a little more):
    def collide(self):
        WindSim.rho = (WindSim.n0 + WindSim.nN + WindSim.nS +
                       WindSim.nE + WindSim.nW + WindSim.nNE +
                       WindSim.nSE + WindSim.nNW + WindSim.nSW)
        WindSim.ux = (WindSim.nE + WindSim.nNE + WindSim.nSE -
                      WindSim.nW - WindSim.nNW - WindSim.nSW) / WindSim.rho
        WindSim.uy = (WindSim.nN + WindSim.nNE + WindSim.nNW -
                      WindSim.nS - WindSim.nSE - WindSim.nSW) / WindSim.rho
        ux2 = WindSim.ux * WindSim.ux  # pre-compute terms used repeatedly...
        uy2 = WindSim.uy * WindSim.uy
        u2 = ux2 + uy2
        omu215 = 1 - 1.5 * u2  # "one minus u2 times 1.5"
        uxuy = WindSim.ux * WindSim.uy
        WindSim.n0 = ((1 - WindSim.omega) * WindSim.n0 +
                      WindSim.omega * WindSim.four9ths * WindSim.rho * omu215)
        WindSim.nN = ((1 - WindSim.omega) * WindSim.nN +
                      WindSim.omega * WindSim.one9th * WindSim.rho *
                      (omu215 + 3 * WindSim.uy + 4.5 * uy2))
        WindSim.nS = ((1 - WindSim.omega) * WindSim.nS +
                      WindSim.omega * WindSim.one9th * WindSim.rho *
                      (omu215 - 3 * WindSim.uy + 4.5 * uy2))
        WindSim.nE = ((1 - WindSim.omega) * WindSim.nE +
                      WindSim.omega * WindSim.one9th * WindSim.rho *
                      (omu215 + 3 * WindSim.ux + 4.5 * ux2))
        WindSim.nW = ((1 - WindSim.omega) * WindSim.nW +
                      WindSim.omega * WindSim.one9th * WindSim.rho *
                      (omu215 - 3 * WindSim.ux + 4.5 * ux2))
        WindSim.nNE = ((1 - WindSim.omega) * WindSim.nNE +
                       WindSim.omega * WindSim.one36th * WindSim.rho *
                       (omu215 + 3 * (WindSim.ux + WindSim.uy) +
                        4.5 * (u2 + 2 * uxuy)))
        WindSim.nNW = ((1 - WindSim.omega) * WindSim.nNW +
                       WindSim.omega * WindSim.one36th * WindSim.rho *
                       (omu215 + 3 * (-WindSim.ux + WindSim.uy) +
                        4.5 * (u2 - 2 * uxuy)))
        WindSim.nSE = ((1 - WindSim.omega) * WindSim.nSE +
                       WindSim.omega * WindSim.one36th * WindSim.rho *
                       (omu215 + 3 * (WindSim.ux - WindSim.uy) +
                        4.5 * (u2 - 2 * uxuy)))
        WindSim.nSW = ((1 - WindSim.omega) * WindSim.nSW +
                       WindSim.omega * WindSim.one36th * WindSim.rho *
                       (omu215 + 3 * (-WindSim.ux - WindSim.uy) +
                        4.5 * (u2 + 2 * uxuy)))
        # Force steady rightward flow at ends
        # (no need to set 0, N, and S components):
        WindSim.nE[:, 0] = (WindSim.one9th *
                            (1 + 3 * WindSim.u0 +
                             4.5 * WindSim.u0**2 -
                             1.5 * WindSim.u0**2))
        WindSim.nW[:, 0] = (WindSim.one9th *
                            (1 - 3 * WindSim.u0 +
                             4.5 * WindSim.u0**2 -
                             1.5 * WindSim.u0**2))
        WindSim.nNE[:, 0] = (WindSim.one36th *
                             (1 + 3 * WindSim.u0 +
                              4.5 * WindSim.u0**2 -
                              1.5 * WindSim.u0**2))
        WindSim.nSE[:, 0] = (WindSim.one36th *
                             (1 + 3 * WindSim.u0 +
                              4.5 * WindSim.u0**2 -
                              1.5 * WindSim.u0**2))
        WindSim.nNW[:, 0] = (WindSim.one36th *
                             (1 - 3 * WindSim.u0 +
                              4.5 * WindSim.u0**2 -
                              1.5 * WindSim.u0**2))
        WindSim.nSW[:, 0] = (WindSim.one36th *
                             (1 - 3 * WindSim.u0 +
                              4.5 * WindSim.u0**2 -
                              1.5 * WindSim.u0**2))

    def get_streamline(self, _y):
        x, y = self.follow_through(WindSim.ux, WindSim.uy, _y)
        if self.PLOT_INDIVIDUAL_STREAMLINES:
            plt.clf()
            plt.plot(x, y)
            xRange = range(0, 200)
            yRange = range(0, 200)
            plt.plot(xRange, yRange)
            plt.savefig("output/streamline_at_" + str(_y) + ".png")
        return (x, y)

    def follow_through(self, ux, uy, start_y=0):
        x0 = 0
        y0 = start_y
        x = [x0]
        y = [y0]

        try:
            counter = 10000
            while counter > 1:
                xRun = ux[round(y[-1]), round(x[-1])]  # + 0.0045
                if xRun < 0:
                    counter = 0
                    print("cancelled line: line ends early")
                yRun = uy[round(y[-1]), round(x[-1])]

                travel_distance = (xRun ** 2 + yRun ** 2) ** 0.5
                x.append((x[-1] + xRun / travel_distance / 2))
                y.append((y[-1] + yRun / travel_distance / 2))

                counter -= 1
        except Exception as e:
            print e
        print ("Counter: {0}".format(counter))
        return (x, y)

    # Compute curl of the macroscopic velocity field:
    def curl(self, ux, uy):
        return (np.roll(uy, -1, axis=1) -
                np.roll(uy, 1, axis=1) -
                np.roll(ux, -1, axis=0) +
                np.roll(ux, 1, axis=0))

    def nextFrame(self, arg):
        # (arg is the frame number, which we don't need)
        self.frame_c += 1
        print("computed frame:" + str(self.frame_c))
        if WindSim.performanceData and (arg % 30 == 0) and (arg > 0):
            endTime = clock()
            print ("Took {0} seconds".format(endTime - self.startTime))
            print ("%1.1f" % (30 / (endTime - self.startTime)),
                   'frames per second')
            self.startTime = endTime
            if (WindSim.save):
                frameName = 'output/frame%04d.png' % arg
                plt.savefig(frameName)
                self.frameList.write(frameName + '\n')
        for step in range(WindSim.step_range):
            self.stream()
            self.collide()
        self.fluidImage.set_array(self.curl(WindSim.ux, WindSim.uy))
        return (self.fluidImage, self.barrierImage)
