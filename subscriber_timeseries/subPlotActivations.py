from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import gridplot, row, layout, column
import numpy as np
import time
import cProfile
import random
import zmq
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

data_collection_buffer = []

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
    global socket_sub, poller, data_collection_buffer
    try:
        print('add to buffer')
        data_collection_buffer += [poll_via_zmq_socket_subscriber(socket_sub, poller)]
    except KeyboardInterrupt:
        print("CLEAN UP CLEAN UP EVERYBODY CLEANUP")
        while not socket_sub.closed:
            print("close the socket!")
            socket_sub.close()
    buffer_size = len(data_collection_buffer)
    
    if buffer_size > 100:
        print('buffer overflowed.')
        for i in range(0, buffer_size):
            print('streaming buffer_i, i=%s' % i)
            source.stream(data_collection_buffer[i], 100)
        data_collection_buffer = [] #clear


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

def update():
    global main_layout
    for i in range(7):
        main_layout.children[i] = create_figline()[i]




socket_sub = initialize_sub_socket(ip, port_sub)
poller = zmq.Poller()
print("Latency")
doc = curdoc()
doc.add_periodic_callback(update, 1)
main_layout = column(create_figline())
doc.add_root(main_layout)
