import zmq
import pickle
import time
import numpy as np
from bokeh.layouts import layout, row, gridplot
import bokeh
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
import random

source = ColumnDataSource(dict(x=[], muscle_0=[], muscle_1=[], muscle_2=[]))

def initialize_sub_socket(ip, port, topic_filter=b"map"):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket_string = "%s:%s" % (ip, port)
    #print("Connecting to %s" % socket_string)
    #you can run this multiple times to receive from multiple ports
    socket.connect("tcp://%s:%s" %(ip, port))
    socket.setsockopt_string(zmq.SUBSCRIBE,'')
    #print('Set ZMQ Subscriber with topic filter')
    return(socket)

ctr = []
def update_data():
    global ctr, socket
    [topic, msg] = socket.recv_multipart()
    message = pickle.loads(msg, encoding="latin1")
    #print("MESSAGE", message)

    ctr = list(range(len(message[0][0])))
    # measuredForces = message[0][0]
    # targetForces = message[0][1]
    # commands = message[0][2]

    new_data = dict(x=[ctr], muscle_0=[message[0][0]], muscle_1=[message[0][1]], muscle_2 = [message[0][2]])
    source.stream(new_data,10)
    #print("streamed data: ",source.data['x'], source.data['y'])


def update():
    #plots = (generate_figure())
    for i in range(3):
        layout.children[i] = generate_figure()[i]

def generate_figure():
    global source
    ip = '127.0.0.1'
    port = '12345'
    socket = initialize_sub_socket(ip, port)
    update_data()
    colors = ["#762a83","#76EEC6","#53868B","#FF1493","#ADFF2F","#292421","#FFE1FF"]
    figlist = []
    #fig = figure(plot_width=250, plot_height=250, title=None)
    for i in range(3):
        global figlist
        fig = figure(plot_width=250, plot_height=250, title=None)
        muscle = 'muscle_%s' %i
        hist, edges = np.histogram(source.data[muscle])
        fig.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color=colors[i])
        figlist.append(fig)

    return (figlist)

ip = '127.0.0.1'
port = '12345'
socket = initialize_sub_socket(ip, port)

layout = row(generate_figure())
curdoc().add_periodic_callback(update, 1)
curdoc().add_root(layout)
