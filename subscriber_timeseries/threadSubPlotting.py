from functools import partial
from random import random
from threading import Thread
import time

from bokeh.layouts import gridplot, row, layout, column
from bokeh.models import ColumnDataSource
from bokeh.plotting import curdoc, figure
from bokeh.models import LinearAxis, Range1d
from bokeh.models import Span

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
    source.stream(data_collection_buffer,250)

def modify_to_plot(messagedata):
    '''These are not the actual forces in newtons
        Modified to accomodate in a single graph'''
    gap = 1.0
    for i in range(7):
        messagedata['measured_M%s' % i] = [(messagedata['measured_M%s' % i][0]+(i)*gap)]
        messagedata['reference_M%s' % i] = [(messagedata['reference_M%s' % i][0]+(i)*gap)]
    return messagedata

def subscribe_and_stream():
    while True:
        # do some blocking computation
        #time.sleep(0.1)
        global socket_sub, poller, data_collection_buffer, source
        try:
            messagedata = poll_via_zmq_socket_subscriber(socket_sub, poller)
            # but update the document from callback
            modifiedMsgData = modify_to_plot(messagedata)
            doc.add_next_tick_callback(partial(update, modifiedMsgData))

        except KeyboardInterrupt:
            print("CLEAN UP CLEAN UP EVERYBODY CLEANUP")
            while not socket_sub.closed:
                print("close the socket!")
                socket_sub.close()


colors = ["#762a83", "#76EEC6", "#53868B",
          "#FF1493", "#ADFF2F", "#292421", "#EE6A50"]

fig = figure(plot_width=2000, plot_height=750, y_range=(0,7))

lower_lt = 0.5
upper_lt = 1.5
for muscle_index in range(7):
    loc = ((muscle_index+1)*lower_lt + (muscle_index+1)*upper_lt)/2.0
    line = Span(location=loc, dimension='width', line_color='black', line_dash='dashed', line_width=1)
    fig.add_layout(line)
    fig.line(source=source, x='time', y='measured_M%s' % muscle_index,
             line_width=2, alpha=0.85, color=colors[muscle_index])
    fig.line(source=source, x='time', y='reference_M%s' %muscle_index, line_width=2, alpha=0.85, color='blue')

doc.add_root(fig)

socket_sub = initialize_sub_socket(ip, port_sub)
poller = zmq.Poller()

thread = Thread(target=subscribe_and_stream)
thread.start()
