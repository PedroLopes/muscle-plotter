'''A mouse-anoto emulator based on Tk.

Example:
  Run with the command as follows and you can input the frame with mouse.
    $ python anoto_mouse_emulator

  Close the frame to shut down the script.

Configuration:
  Use the toolbox (right side of window) to configure:
    OSC address and/or port,
    start OSC client (starts sending mouse data to muscle-plotter)
    enable debug prints (on your command line / terminal)
    enable windtunnel debug (i.e., see canvas where to draw)

Warning:
  Check this out if you want to run this on a mac in the virtualenv.
  tkinter installs with macports not in default virtual env directories.
  http://lab.openpolis.it/using-tkinter-inside-a-virtualenv.html

'''
import context as ct

import Tkinter as Tk
import OSC
import time
import argparse

# OSC connection details
OSC_default_port = 5103
OSC_default_address = "127.0.0.1"
OSC_connection = False 

# state of mouse starts as not pressed
mouse_down = False

# Anoto paper coordinates (you might need to adjust to your particular brand of paper)
starting_point_x = 200
end_x = 6400
starting_point_y = 200
end_y = 8300

# window size
width = 560
height = 730

# toolbox / mini GUI
toolbox_width = 150
toolbox_height = 100
toolbox_padding_y = 20
toolbox_padding_x = 10
windtunnel_on = False

# arguments
parser = argparse.ArgumentParser(description='a OSC mouse emulator used for muscle-plotter', epilog="muscle-plotter is documented at https://github.com/PedroLopes/muscle-plotter")
parser.add_argument('--start', action='store_true', dest='OSC_connection', help='automatically starts the client (connects to socket)')
parser.add_argument('--wind', action='store_true', dest='windtunnel_on', help='draws the test windtunnel canvas (visual debug)')
parser.add_argument('--address', action='store', dest='OSC_default_address', help='OSC address to send to (default: ' + str(OSC_default_address) + ')')
parser.add_argument('--port', action='store', dest='OSC_default_port', help='OSC port to send to (default: ' + str(OSC_default_port) + ')')
args = parser.parse_args()
if (args.OSC_default_port):
    OSC_default_port = args.OSC_default_port
if (args.OSC_default_address):
    OSC_default_address = args.OSC_default_address
if (args.OSC_connection):
    OSC_connection = args.OSC_connection
if (args.windtunnel_on):
     windtunnel_on= args.windtunnel_on

def point_transform(x, y):
    new_x = ct.remap(x, 0, width, starting_point_x, end_x)
    new_y = ct.remap(y, 0, height, starting_point_y, end_y)
    return new_x, new_y

def reverse_transform(x,y):
    new_x = ct.remap(x, starting_point_x, end_x, 0, width,)
    new_y = ct.remap(y, starting_point_y, end_y, 0, height)
    return new_x, new_y

# windtunnel placement (for a test tunnel)
sketch_area_width = 4300
sketch_area_height = 4300
sketch_area_left_down = [1700, 5300]
sketch_area_right_down = [sketch_area_left_down[0] + sketch_area_width,
                          sketch_area_left_down[1]]
sketch_area_right_up = [sketch_area_right_down[0],
                        sketch_area_right_down[1] - sketch_area_height]
sketch_area_left_up = [sketch_area_left_down[0],
                       sketch_area_right_down[1] - sketch_area_height]
sketch_area_left_up = reverse_transform(sketch_area_left_up[0], sketch_area_left_up[1])
sketch_area_right_down = reverse_transform(sketch_area_right_down[0], sketch_area_right_down[1])

strokes = []

def motion(event):
    global mouse_down
    global master
    global toolbox_debug_prints
    if mouse_down:
        if (toolbox_debug_prints.var.get()): print("mouse/X:%s  mouse/Y/%s)" % (event.x, event.y))
        xy = point_transform(event.x, event.y)
        if (OSC_connection): osc_server.send_message(xy, event='drag')
        add_stroke(event.x,event.y)

def add_stroke(x,y):
    global strokes
    global toolbox_strokes_visible
    if not toolbox_strokes_visible.var.get():
        return
    else:
        temp_point =  canvas.create_rectangle(x-1, y-1, x+1, y+1, fill="black",state="normal")
        strokes.append(temp_point)

def buttonPressed(event):
    global mouse_down
    global master
    global toolbox_debug_prints
    mouse_down = True
    if (toolbox_debug_prints.var.get()): 
        print("mouse/down")
        print("mouse/X:%s  mouse/Y/%s)" % (event.x, event.y))
    xy = point_transform(event.x, event.y)
    if (OSC_connection): osc_server.send_message(xy, event='down')
    add_stroke(event.x,event.y)
    

def buttonReleased(event):
    global mouse_down
    global master
    global toolbox_debug_prints
    mouse_down = False
    if (toolbox_debug_prints.var.get()): 
        print("mouse/up")
        print("mouse/X:%s  mouse/Y/%s)" % (event.x, event.y))
    xy = point_transform(event.x, event.y)
    if (OSC_connection): osc_server.send_message(xy, event='up')
    add_stroke(event.x,event.y)


class FakeClient(object):
    """Sends timed messages to imitate anoto server.

    """
    def __init__(self):
        super(FakeClient, self).__init__()
        self.listen_address = (OSC_default_address, OSC_default_port)
        self.c = OSC.OSCClient()

    def compose_address(self):
        self.listen_address = (OSC_default_address, OSC_default_port)

    def send_message(self, point, event='drag', rest=0.012):
        x, y = point
        message = OSC.OSCMessage()
        message.setAddress("/anoto")
        message.append(x)
        message.append(y)
        message.append(event)
        message.append(self.time)
        self.time += (rest * 1000)
        while self.time > 100:
            self.time -= 100
        self.c.send(message)
        time.sleep(rest)

    def close_client(self):
        self.c.close()

    def start_client(self):
        self.compose_address()
        self.c.connect(self.listen_address)
        self.time = 2


def toggle_OSC():
    global osc_server
    global OSC_connection 
    OSC_connection = not OSC_connection
    if (OSC_connection):
        osc_server.start_client()
    else:
        osc_server.close_client()

def toggle_windtunnel():
    global windtunnel_on
    global windtunnel_boundary
    windtunnel_on = not windtunnel_on
    if (windtunnel_on):
        canvas.itemconfig(windtunnel_boundary, state="normal")
    else:
        canvas.itemconfig(windtunnel_boundary, state="hidden")
        

# configure the TK window
master = Tk.Tk()
master.resizable(width=Tk.FALSE, height=Tk.FALSE)
master.geometry('{}x{}'.format(width+toolbox_width, height))

# add a canvas for mouse tracking
canvas = Tk.Canvas(master, width=width, height=height)
canvas.config(cursor='cross red red')
canvas.pack()
canvas.config(highlightbackground="grey")
windtunnel_boundary = canvas.create_rectangle(sketch_area_left_up[0], sketch_area_left_up[1], sketch_area_right_down[0], sketch_area_right_down[1], fill="white",state="hidden")
canvas.bind('<Motion>', motion)
canvas.bind("<Button-1>", buttonPressed)
canvas.bind("<ButtonRelease-1>", buttonReleased)
canvas.place(x=0, y=0, anchor="nw")

# add checkbox variables
debug_prints = Tk.IntVar()
strokes_visible = Tk.IntVar()
strokes_visible.set(1)

# subsection/OSC config
toolbox_OSC_label = Tk.Label(master, text="OSC options")
toolbox_OSC_connection = Tk.Checkbutton(master, text="connect client", command=toggle_OSC)
toolbox_OSC_address = Tk.Text(master, height=1, width=15)
toolbox_OSC_address.insert(Tk.END, OSC_default_address)
toolbox_OSC_port = Tk.Text(master, height=1, width=15)
toolbox_OSC_port.insert(Tk.END, OSC_default_port)

# subsection/debug add checkboxes
toolbox_debug_label = Tk.Label(master, text="Debug options")
toolbox_debug_prints = Tk.Checkbutton(master, text="prints (CLI)", variable=debug_prints)
toolbox_strokes_visible = Tk.Checkbutton(master, text="show strokes", variable=strokes_visible)
#toolbox_debug_mouse = Tk.Checkbutton(master, text="mouse trace", variable=debug_motion)
toolbox_debug_windtunnel_canvas = Tk.Checkbutton(master, text="windtunnel", command=toggle_windtunnel)
toolbox_debug_prints.var = debug_prints
toolbox_strokes_visible.var = strokes_visible
#toolbox_debug_mouse.var = debug_motion
#toolbox_debug_windtunnel_canvas.var = debug_windtunnel_canvas

# pack OSC in order
toolbox_OSC_label.pack()
toolbox_OSC_connection.pack()
toolbox_OSC_address.pack()
toolbox_OSC_port.pack()

# pack debug in order
toolbox_debug_label.pack()
toolbox_OSC_connection.pack()
toolbox_debug_prints.pack()
toolbox_strokes_visible.pack()
#toolbox_debug_mouse.pack()
toolbox_debug_windtunnel_canvas.pack()

# place all
toolbox_OSC_label.place(x=width+toolbox_padding_x, y=toolbox_padding_y*0, anchor="nw")
toolbox_OSC_connection.place(x=width+toolbox_padding_x, y=toolbox_padding_y*1, anchor="nw")
toolbox_OSC_address.place(x=width+toolbox_padding_x, y=toolbox_padding_y*2, anchor="nw")
toolbox_OSC_port.place(x=width+toolbox_padding_x, y=toolbox_padding_y*3, anchor="nw")
toolbox_debug_label.place(x=width+toolbox_padding_x, y=toolbox_padding_y*5, anchor="nw")
toolbox_debug_prints.place(x=width+toolbox_padding_x, y=toolbox_padding_y*6, anchor="nw")
toolbox_strokes_visible.place(x=width+toolbox_padding_x, y=toolbox_padding_y*7, anchor="nw")
toolbox_debug_windtunnel_canvas.place(x=width+toolbox_padding_x, y=toolbox_padding_y*8, anchor="nw")
#toolbox_debug_mouse.place(x=width+toolbox_padding_x, y=toolbox_padding_y*8, anchor="nw")

# create the server
osc_server = FakeClient()

# configure the GUI CLI arguments prior to start 
if (args.OSC_connection):
    OSC_connection = False
    toolbox_OSC_connection.invoke()
if (args.windtunnel_on):
    windtunnel_on = False
    toolbox_debug_windtunnel_canvas.invoke()

# start the GUI
Tk.mainloop()
