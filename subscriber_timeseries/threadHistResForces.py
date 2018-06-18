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

source = ColumnDataSource(dict(time=[],residual_M0=[],residual_M1=[],residual_M2=[],residual_M3=[],residual_M4=[],residual_M5=[],residual_M6=[]))

doc = curdoc()

@gen.coroutine
def update(modifiedHistData):
    source.stream(modifiedHistData,100)

def modify_to_plot(messagedata):
    '''These are not the actual forces in newtons
        Modified to accomodate in a single graph'''
    gap = 1.0
    for i in range(7):
        messagedata['residual_M%s' % i] = [(messagedata['residual_M%s' % i][0]+(i)*gap)]
    print("messagedata", messagedata)
    return messagedata

def subscribe_and_stream():
    while True:
        global socket_sub
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
                #global edges
                #hist, edges = np.histogram(residualForces)
                messagedata = dict(time=[timestamp],residual_M0=[residualForces[0]],residual_M1=[residualForces[1]],residual_M2=[residualForces[2]],residual_M3=[residualForces[3]],residual_M4=[residualForces[4]],residual_M5=[residualForces[5]],residual_M6=[residualForces[6]])
                # dict(residual_M0=[hist[0]],residual_M1=[hist[1]],residual_M2=[hist[2]],residual_M3=[hist[3]],residual_M4=[hist[4]],hist=[residualForces[5]],residual_M6=[hist[6]])
                # #print(new_data)

                modifiedHistData = modify_to_plot(messagedata)
                doc.add_next_tick_callback(partial(update, modifiedHistData))

        except KeyboardInterrupt:
            print("CLEAN UP CLEAN UP EVERYBODY CLEANUP")
            while not socket_sub.closed:
                make_clean_exit(socket_sub)



colors = ["#762a83", "#76EEC6", "#53868B",
          "#FF1493", "#ADFF2F", "#292421", "#EE6A50"]

fig = figure(plot_width=2000, plot_height=750, y_range=(0,7))

lower_lt = 0.5
upper_lt = 1.5
for muscle_index in range(7):
    muscle = 'residual_M%s' %muscle_index
    loc = ((muscle_index+1)*lower_lt + (muscle_index+1)*upper_lt)/2.0
    line = Span(location=loc, dimension='width', line_color='black', line_dash='dashed', line_width=1)
    fig.add_layout(line)
    #fig.line(source=source, x='time', y='residual_M%s' % muscle_index,line_width=2, alpha=0.85, color=colors[muscle_index])

    #data_values = stats[ column ].tolist()
    hist, edges = np.histogram(source.data[muscle])
    fig.quad(top='residual_M%s' % muscle_index, bottom=0, left=edges[:-1], right=edges[1:], fill_color=colors[muscle_index])

doc.add_root(fig)

socket_sub = initialize_sub_socket(ip, port_sub)
print("Plotting Histogram...")

thread = Thread(target=subscribe_and_stream)
thread.start()
