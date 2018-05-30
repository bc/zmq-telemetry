from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import gridplot, row
import numpy as np
import time
import cProfile
import random
import zmq
import pickle


def initialize_sub_socket(ip, port, topic_filter=b"map"):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket_string = "%s:%s" % (ip, port)
    print("Connecting to %s" % socket_string)
    #you can run this multiple times to receive from multiple ports
    socket.connect("tcp://%s:%s" %(ip, port))
    socket.setsockopt(zmq.SUBSCRIBE, topic_filter)
    print('Set ZMQ Subscriber with topic filter')
    return(socket)

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

# fig1 = figure()
# fig1.line(x='time', y='measured_M0', source=source, line_width=2, alpha=0.85, color='red')
# fig1.line(x='time', y='reference_M0', source=source, line_width=2, alpha=0.85, color='blue')

def update_data():
    global socket
    try:
        [topic, msg] = socket.recv_multipart()
        #print("VALUES", msg)
        message = (pickle.loads(msg, encoding="latin1"))
        #print("values", message)
        measuredForces = message[0][0]
        referenceForces = message[0][1]
        #residualForces = [message[0][0][i]-message[0][1][i] for i in range(7)]
        commands = message[0][2]
        timestamp = message[1]

        new_data = dict(time=[timestamp],measured_M0=[measuredForces[0]],measured_M1=[measuredForces[1]],measured_M2=[measuredForces[2]],measured_M3=[measuredForces[3]],measured_M4=[measuredForces[4]],measured_M5=[measuredForces[0]],measured_M6=[measuredForces[6]],reference_M0=[referenceForces[0]],reference_M1=[referenceForces[1]],reference_M2=[referenceForces[2]],reference_M3=[referenceForces[3]],reference_M4=[referenceForces[4]],reference_M5=[referenceForces[5]],reference_M6=[referenceForces[6]])

        source.stream(new_data, 100)

    except KeyboardInterrupt:
        socket.close()

def update():
    global main_layout
    for i in range(7):
        main_layout.children[i] = create_figline()[i]

def create_figline():
    global source
    update_data()
    colors = ["#762a83","#76EEC6","#53868B","#FF1493","#ADFF2F","#292421","#FFE1FF"]
    figlist = []
    for muscle_index in range(7):
        fig = figure(plot_width=250, plot_height=250, title=None)
        fig.line(source=source, x='time', y='measured_M%s' %muscle_index, line_width=2, alpha=0.85, color=colors[muscle_index])
        fig.line(source=source, x='time', y='reference_M%s' %muscle_index, line_width=2, alpha=0.85, color='blue')
        figlist.append(fig)
    return figlist

ip = '127.0.0.1'
port = '12345'
socket = initialize_sub_socket(ip, port)


curdoc().add_periodic_callback(update, 1)
main_layout = row(create_figline())
curdoc().add_root(main_layout)
