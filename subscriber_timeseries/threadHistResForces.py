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

source_forces = ColumnDataSource(dict(time=[],residual_M0=[],residual_M1=[],residual_M2=[],residual_M3=[],residual_M4=[],residual_M5=[],residual_M6=[]))
source_plot = ColumnDataSource(dict(hist_M0=[],hist_M1=[],hist_M2=[],hist_M3=[],hist_M4=[],hist_M5=[],hist_M6=[],ledges_M0=[], ledges_M1=[], ledges_M2=[], ledges_M3=[], ledges_M4=[], ledges_M5=[], ledges_M6=[], redges_M0=[], redges_M1=[], redges_M2=[], redges_M3=[], redges_M4=[], redges_M5=[], redges_M6=[]))

@gen.coroutine
def update(plotData,residualForces):
    source_forces.stream(residualForces,100)
    source_plot.stream(plotData,100)

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
                    histogram  = np.histogram(source_forces.data['residual_M%s'%i])
                    for j in range(len(histogram[1])):
                        histogram[1][j] = (histogram[1][j] + i*1)
                    print("histogram[1]",histogram[1])
                    hist.append(histogram[0])
                    edges.append(histogram[1])

                residualForces = dict(time=[timestamp],residual_M0=[residualForces[0]],residual_M1=[residualForces[1]],residual_M2=[residualForces[2]],residual_M3=[residualForces[3]],residual_M4=[residualForces[4]],residual_M5=[residualForces[5]],residual_M6=[residualForces[6]])

                plotData =  dict(hist_M0=hist[0].tolist(),hist_M1=hist[1].tolist(),hist_M2=hist[2].tolist(),hist_M3=hist[3].tolist(),hist_M4=hist[4].tolist(),hist_M5=hist[5].tolist(),hist_M6=hist[6].tolist(),ledges_M0=edges[0][:-1].tolist(),ledges_M1=edges[1][:-1].tolist(),ledges_M2=edges[2][:-1].tolist(),ledges_M3=edges[3][:-1].tolist(),ledges_M4=edges[4][:-1].tolist(),ledges_M5=edges[5][:-1].tolist(),ledges_M6=edges[6][:-1].tolist(),redges_M0=edges[0][1:].tolist(),redges_M1=edges[1][1:].tolist(),redges_M2=edges[2][1:].tolist(),redges_M3=edges[3][1:].tolist(),redges_M4=edges[4][1:].tolist(),redges_M5=edges[5][1:].tolist(),redges_M6=edges[6][1:].tolist())

                #print(messagedata)

                doc.add_next_tick_callback(partial(update,plotData,residualForces))

        except KeyboardInterrupt:
            print("CLEAN UP CLEAN UP EVERYBODY CLEANUP")
            while not socket_sub.closed:
                make_clean_exit(socket_sub)



colors = ["#762a83", "#76EEC6", "#53868B",
          "#FF1493", "#ADFF2F", "#292421", "#EE6A50"]

gap = 1
fig = figure(plot_width=1400, plot_height=700, x_range=(0,7))
for muscle_index in range(7):
    loc = gap*muscle_index
    line = Span(location=loc, dimension='height', line_color='black', line_dash='dashed', line_width=1)
    fig.add_layout(line)
    fig.quad(source=source_plot, top='hist_M%s'%muscle_index, bottom=0, left='ledges_M%s'%muscle_index, right='redges_M%s'%muscle_index, color=colors[muscle_index])

doc.add_root(fig)
socket_sub = initialize_sub_socket(ip, port_sub)
print("Plotting Histogram...")

thread = Thread(target=subscribe_and_stream)
thread.start()
