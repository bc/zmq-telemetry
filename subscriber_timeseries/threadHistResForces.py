from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import gridplot, row, layout, column

import numpy as np
import time
import cProfile
import random
import zmq
import pickle
import pdb
import time

from bokeh.models import LinearAxis, Range1d
from bokeh.models import Span
from functools import partial
from threading import Thread
from tornado import gen
from helper_functions import *

rpi_emulator = True
brian = False

if rpi_emulator:
    ip = '127.0.0.1'
elif brian:
    ip = '169.254.12.240'
else:
    ip = '10.42.0.82'

port_sub = '12345'

doc = curdoc()

@gen.coroutine
def update(residualForces):
    global fig
    #i = 1
    hist = [0 for i in range(7)]
    edges = [0 for i in range(7)]
    for i in range(7):
        hist[i], edges[i] = np.histogram(residualForces[i])
    fig.quad(top=[hist[0],hist[1],hist[2],hist[3],hist[4],hist[5],hist[6]], bottom=[0,1,2,3,4,5,6,], left=[edges[0][:-1],edges[1][:-1],edges[2][:-1],edges[3][:-1],edges[4][:-1],edges[5][:-1],edges[6][:-1]], right=[edges[0][1:],edges[1][1:],edges[2][1:],edges[3][1:],edges[4][1:],edges[5][1:],edges[6][1:]])


hist = []
edges = []
def subscribe_and_stream():
    global fig
    while True:
        global socket_sub, fig
        try:
            poller = zmq.Poller()
            poller.register(socket_sub, zmq.POLLIN)
            socks = dict(poller.poll())

            if socket_sub in socks and socks[socket_sub] == zmq.POLLIN:
                [topic, msg] = socket_sub.recv_multipart()
                message = (pickle.loads(msg, encoding="latin1"))
                #print("values", message)
                measuredForces = message[0][0]
                referenceForces = message[0][1]
                ### using absolute difference ###
                residualForces = [np.abs(message[0][0][i]-message[0][1][i]) for i in range(7)]
                commands = message[0][2]
                timestamp = message[1]
                print("residualForces", residualForces)
                doc.add_next_tick_callback(partial(update,residualForces))

        except KeyboardInterrupt:
            print("CLEAN UP CLEAN UP EVERYBODY CLEANUP")
            while not socket_sub.closed:
                make_clean_exit(socket_sub)



colors = ["#762a83", "#76EEC6", "#53868B",
          "#FF1493", "#ADFF2F", "#292421", "#EE6A50"]

muscle_index = 0
fig = figure(plot_width=2000, plot_height=750, y_range=(0,7))

doc.add_root(fig)
socket_sub = initialize_sub_socket(ip, port_sub)
print("Plotting Histogram...")

thread = Thread(target=subscribe_and_stream)
thread.start()
