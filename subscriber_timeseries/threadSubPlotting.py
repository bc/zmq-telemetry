from functools import partial
from random import random
from threading import Thread
import time

from bokeh.layouts import gridplot, row, layout, column
from bokeh.models import ColumnDataSource
from bokeh.plotting import curdoc, figure

from tornado import gen
from helper_functions import *

ip = '127.0.0.1'
port_sub = '12345'

# this must only be modified from a Bokeh session callback
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

# This is important! Save curdoc() to make sure all threads
# see the same document.
doc = curdoc()

@gen.coroutine
def update(data_collection_buffer):
    source.stream(data_collection_buffer,100)

def blocking_task():
    while True:
        # do some blocking computation
        time.sleep(0.1)
        x, y = random(), random()
        global socket_sub, poller, data_collection_buffer, source
        try:
            print('add to buffer')
            data_collection_buffer = poll_via_zmq_socket_subscriber(socket_sub, poller)
            # but update the document from callback
            doc.add_next_tick_callback(partial(update, data_collection_buffer))

        except KeyboardInterrupt:
            print("CLEAN UP CLEAN UP EVERYBODY CLEANUP")
            while not socket_sub.closed:
                print("close the socket!")
                socket_sub.close()


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
doc.add_root(column(figlist))

socket_sub = initialize_sub_socket(ip, port_sub)
poller = zmq.Poller()

thread = Thread(target=blocking_task)
thread.start()
