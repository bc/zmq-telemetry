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

source = ColumnDataSource(dict(hist_M0=[],hist_M1=[],hist_M2=[],hist_M3=[],hist_M4=[],hist_M5=[],hist_M6=[],ledges_M0=[], ledges_M1=[], ledges_M2=[], ledges_M3=[], ledges_M4=[], ledges_M5=[], ledges_M6=[], redges_M0=[], redges_M1=[], redges_M2=[], redges_M3=[], redges_M4=[], redges_M5=[], redges_M6=[]))

@gen.coroutine
def update(residualForces):
    source.stream(residualForces,100)

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
                #print("residualForces", residualForces)
                hist = []
                edges = []
                for i in range(7):
                    histogram  = np.histogram(residualForces[i])
                    hist.append(histogram[0])
                    edges.append(histogram[1])
                print("HIST",hist[0][0],type(hist[0][0]))
                #print("edges",edges)
                messagedata =  dict(hist_M0=hist[0].tolist(),hist_M1=hist[1].tolist(),hist_M2=hist[2].tolist(),hist_M3=hist[3].tolist(),hist_M4=hist[4].tolist(),hist_M5=hist[5].tolist(),hist_M6=hist[6].tolist(),ledges_M0=edges[0][:-1].tolist(),ledges_M1=edges[1][:-1].tolist(),ledges_M2=edges[2][:-1].tolist(),ledges_M3=edges[3][:-1].tolist(),ledges_M4=edges[4][:-1].tolist(),ledges_M5=edges[5][:-1].tolist(),ledges_M6=edges[6][:-1].tolist(), redges_M0=edges[0][1:].tolist(),redges_M1=edges[1][1:].tolist(),redges_M2=edges[2][1:].tolist(),redges_M3=edges[3][1:].tolist(),redges_M4=edges[4][1:].tolist(),redges_M5=edges[5][1:].tolist(),redges_M6=edges[6][1:].tolist())

                print(messagedata)

                doc.add_next_tick_callback(partial(update,messagedata))

        except KeyboardInterrupt:
            print("CLEAN UP CLEAN UP EVERYBODY CLEANUP")
            while not socket_sub.closed:
                make_clean_exit(socket_sub)



colors = ["#762a83", "#76EEC6", "#53868B",
          "#FF1493", "#ADFF2F", "#292421", "#EE6A50"]

muscle_index = 0
fig = figure(plot_width=2000, plot_height=750, y_range=(0,7))
fig.quad(top='hist_M0',bottom=0,left='ledges_M0',right='redges_M0',source=source)

doc.add_root(fig)
socket_sub = initialize_sub_socket(ip, port_sub)
print("Plotting Histogram...")

thread = Thread(target=subscribe_and_stream)
thread.start()
