from __future__ import print_function
import threading
import OSC
from tracespeed import TraceSpeed
import sys
if (sys.version_info < (3, 0)):
    import ConfigParser
    config = ConfigParser.ConfigParser()
else:
    import configparser
    config = configparser.ConfigParser()
config.read('configuration/defaults.cfg')

DEBUG = False


class Anoto(object):
    """
    Manages Bare Pen Communication
    """

    def __init__(self, FAKE_CONNECTION=None):
        super(Anoto, self).__init__()

        if FAKE_CONNECTION is None:
            FAKE_CONNECTION = config.getboolean('Anoto Server',
                                                'fake_connection')
        self.speed = TraceSpeed()
        self.keep_serving = True

        if not FAKE_CONNECTION:
            receive_address = (config.get('Anoto Server', 'receive_ip'),
                               config.getint('Anoto Server', 'receive_port'))
            # self.osc_server = OSC.OSCServer(receive_address)  # basic
            self.osc_server = OSC.ThreadingOSCServer(receive_address)
        else:
            receive_address = (config.get('Anoto Server', 'fake_receive_ip'),
                               config.getint('Anoto Server', 'receive_port'))
            self.osc_server = OSC.ThreadingOSCServer(receive_address)
        # either way - print tracebacks
        self.osc_server.print_tracebacks = True

    def set_callback_function(self, callback):

        # adding our function
        self.osc_server.addMsgHandler("/anoto", self.extend_callback(callback))
        # for addr in osc_server.getOSCAddressSpace(): print addr

    def extend_callback(self, callback):

        def append_prototype(addr, tags, stuff, source):

            if DEBUG:
                print("x: " + str(stuff[0]))
                print("y: " + str(stuff[1]))
                print("event: " + str(stuff[2]) + " on time: " + str(stuff[3]))
            self.speed.feed_data(stuff[0], stuff[1], stuff[3])
            callback(addr, tags, stuff, source)

        return append_prototype

    def start_osc_server(self):

        def serve_long(osc_server):
            '''Target function for OSC Server Thead
            '''
            try:
                while self.keep_serving:
                    osc_server.handle_request()
            except Exception as e:
                if not e.args[0] == 9:
                    raise e

        # Start OSCServer
        if DEBUG:
            print("Starting OSCServer.")
        # self.thread_target = self.osc_server.serve_forever
        self.server_thread = threading.Thread(
            target=serve_long,
            args=(self.osc_server, ))
        self.server_thread.start()
        self.server_thread.setName('OSC Client')

    def close_connection(self):

        if DEBUG:
            print("Closing OSCServer.")
        self.keep_serving = False
        self.osc_server.client.close()
        self.osc_server.server_close()
        if DEBUG:
            print("Waiting for Server-thread to finish")
        self.server_thread.join()
