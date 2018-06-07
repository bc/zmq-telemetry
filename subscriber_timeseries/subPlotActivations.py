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


source = ColumnDataSource(dict(time=[], measured_M0=[],
                               measured_M1=[],
                               measured_M2=[],
                               measured_M3=[],
                               measured_M4=[],
                               measured_M5=[],
                               measured_M6=[],
                               reference_M0=[],
                               reference_M1=[],
                               reference_M2=[],
                               reference_M3=[],
                               reference_M4=[],
                               reference_M5=[],
                               reference_M6=[]))

referenceForces = []
ref_flag = True


def update_data():
    global socket_sub, poller
    try:
        poller.register(socket_sub, zmq.POLLIN)
        socks = dict(poller.poll())
        if socket_sub in socks and socks[socket_sub] == zmq.POLLIN:
            [topic, msg] = socket_sub.recv_multipart()
            message = (pickle.loads(msg, encoding="latin1"))
            measuredForces = message[0][0]
            referenceForces = message[0][1]
            commands = message[0][2]
            timestamp = message[1]
            print("%s" % (str(time.time() - timestamp)))
            # print("## PUBB ##",referenceForces)
            # TODO create a function that returns measured and ref Forces in proper fmt
            new_data = dict(time=[timestamp], measured_M0=[measuredForces[0]], measured_M1=[measuredForces[1]], measured_M2=[measuredForces[2]], measured_M3=[measuredForces[3]], measured_M4=[measuredForces[4]], measured_M5=[measuredForces[0]], measured_M6=[
                            measuredForces[6]], reference_M0=[referenceForces[0]], reference_M1=[referenceForces[1]], reference_M2=[referenceForces[2]], reference_M3=[referenceForces[3]], reference_M4=[referenceForces[4]], reference_M5=[referenceForces[5]], reference_M6=[referenceForces[6]])
            source.stream(new_data, 100)

    except KeyboardInterrupt:
        print("CLEAN UP CLEAN UP EVERYBODY CLEANUP")
        while not socket_sub.closed:
            print("close the socket!")
            socket_sub.close()


def make_clean_exit(socket_sub):
    while not socket_sub.closed:
        print("close the socket!")
        socket_sub.close()


def update():
    global main_layout
    for i in range(7):
        main_layout.children[i] = create_figline()[i]


def create_figline():
    global source
    update_data()
    colors = ["#762a83", "#76EEC6", "#53868B",
              "#FF1493", "#ADFF2F", "#292421", "#EE6A50"]
    figlist = []
    for muscle_index in range(7):
        fig = figure(plot_width=2000, plot_height=180,
                     y_range=(0, 1), title=None)
        fig.line(source=source, x='time', y='measured_M%s' % muscle_index,
                 line_width=2, alpha=0.85, color=colors[muscle_index])
        fig.line(source=source, x='time', y='reference_M%s' %
                 muscle_index, line_width=2, alpha=0.85, color='blue')
        figlist.append(fig)
    return figlist


socket_sub = initialize_sub_socket(ip, port_sub)
poller = zmq.Poller()
print("Latency")
curdoc().add_periodic_callback(update, 1)
main_layout = column(create_figline())
curdoc().add_root(main_layout)
