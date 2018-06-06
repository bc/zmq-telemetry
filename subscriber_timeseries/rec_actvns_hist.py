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


rpi_emulator = True
brian = False

if rpi_emulator:
    ip = '127.0.0.1'
elif brian:
    ip = '169.254.12.240'
else:
    ip = '10.42.0.82'

port_sub = '12345'

def initialize_sub_socket(ip, port_sub, topic_filter=b"map"):
    context = zmq.Context()
    socket_sub = context.socket(zmq.SUB)
    socket_string = "%s:%s" % (ip, port_sub)
    print("Connecting to %s" % socket_string)
    #you can run this multiple times to receive from multiple ports
    socket_sub.connect("tcp://%s:%s" %(ip, port_sub))
    socket_sub.setsockopt(zmq.SUBSCRIBE, topic_filter)
    print('Set ZMQ Subscriber with topic filter')

    return(socket_sub)

source = ColumnDataSource(dict(time=[],residual_M0=[],residual_M1=[],residual_M2=[],residual_M3=[],residual_M4=[],residual_M5=[],residual_M6=[]))


def update_data():
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
            residualForces = [message[0][0][i]-message[0][1][i] for i in range(7)]
            commands = message[0][2]
            timestamp = message[1]
            new_data = dict(time=[timestamp],residual_M0=[residualForces[0]],residual_M1=[residualForces[1]],residual_M2=[residualForces[2]],residual_M3=[residualForces[3]],residual_M4=[residualForces[4]],residual_M5=[residualForces[5]],residual_M6=[residualForces[6]])

            source.stream(new_data, 100)

    except KeyboardInterrupt:
        socket_sub.close()

def update():
    global main_layout
    for i in range(7):
        main_layout.children[i] = create_figline()[i]

def create_figline():
    global source
    update_data()
    colors = ["#762a83","#76EEC6","#53868B","#FF1493","#ADFF2F","#292421","#EE6A50"]
    figlist = []
    for muscle_index in range(7):
        fig = figure(plot_width=600, plot_height=180, title=None)
        muscle = 'residual_M%s' %muscle_index
        hist, edges = np.histogram(source.data[muscle])
        fig.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color=colors[muscle_index])
        figlist.append(fig)
    return figlist

socket_sub = initialize_sub_socket(ip, port_sub)
print("Plotting Histogram...")

curdoc().add_periodic_callback(update, 1)
main_layout = column(create_figline(), sizing_mode='scale_width')
curdoc().add_root(main_layout)
