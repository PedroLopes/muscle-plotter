import sys
import argparse
import subprocess
import time
import threading

from muscleplotter.apps.helpers import validatesInt
from muscleplotter.apps.sinetester import SineTester
from muscleplotter.apps.windtunnel import WindtunnelDemo
from muscleplotter.apps.UserStudy import UserStudy

# setup and arguments
launch_mouse_emulator_on = False
parser = argparse.ArgumentParser(
    description='muscle-plotter: spatial EMS output with pen',
    epilog="muscle-plotter is documented at https://github.com/PedroLopes/muscle-plotter")
parser.add_argument(
    '-m', '--mouse', action='store_true',
    dest='launch_mouse_emulator_on',
    help='launches an OSC mouse emulator for testing')
parser.add_argument(
    '-d', '--demo', action='store', dest='demo_index',
    help='jump starts to a demo (1=sinewaves, 2=windtunnel, 3=user study)',
    type=int)
parser.add_argument(
    '-r', '--remove', action='store_true', dest='clear_temp_files',
    help='Removes all temp files from [output] directory')
args = parser.parse_args()
extra_args = ""

def launch_mouse_emulator():
    time.sleep(3)
    subprocess.call("python " + "tests/anoto_mouse_emulator.py --start " +
                    extra_args, shell=True)

# start muscle-plotter: choose demo scenario
print ("muscle-plotter demos:")
print ('[1] Basic sinewaves\n[2] Windtunnel\n[3] User Study')
not_finished = True

while not_finished:
    if args.demo_index > 0 and args.demo_index <= 3:
        selection = args.demo_index
    else:
        selection = raw_input('Select your application (or q to exit): ')

    if selection == "q":
        print("muscle-plotter closed by user")
        not_finished = False
        sys.exit()

    if validatesInt(selection):
        selection = int(selection)
        if args.clear_temp_files:
            subprocess.call(["rm output/*"], shell=True)
        if args.launch_mouse_emulator_on:
            mouse_emulation = threading.Thread(target=launch_mouse_emulator)
            mouse_emulation.start()
        if selection == 1:
            print('Starting \"Basic sinewaves\" demo')
            not_finished = False
            app = SineTester()
        elif selection == 2:
            print('Starting \"Windtunnel\" demo')
            not_finished = False
            extra_args = "--wind"
            app = WindtunnelDemo()
        elif selection == 3:
            print('Starting \"User Study\"')
            not_finished = False
            app = UserStudy()
        else:
            print('Invalid selection: choose between ' +
                  'the available range [1,3].')
            sys.exit()

try:
    while 1:
        pass
except KeyboardInterrupt:
    if args.launch_mouse_emulator_on :
        mouse_emulation.join()
    app.end_application()
    sys.exit()
