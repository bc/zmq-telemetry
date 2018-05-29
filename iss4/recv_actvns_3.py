from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import row
import numpy as np
import zmq
import pickle
import time


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

source = ColumnDataSource(dict(x=[], measuredForces=[], targetForces=[], commands=[]))

ctr = []
data = []
def update_data():
    global socket
    try:
        [topic, msg] = socket.recv_multipart()
        message = (pickle.loads(msg, encoding="latin1"))
        #print("MESSAGE", message)
        #print("measuredForces=",[message[0][0]], type(message[0][0]))
        ctr = list(range(len(message[0][0])))
        new_data = dict(x=[ctr], measuredForces=[message[0][0]], targetForces=[message[0][1]], commands= [message[0][2]])
        source.stream(new_data)
        return (np.abs(message[0][0] - message[0][1]))
    except KeyboardInterrupt:
        socket.close()


def update():
    global layout
    layout.children[0] = generate_figure()

def generate_figure():
    global source
    residual_error = update_data()
    fig = figure(plot_width=250, plot_height=250, title=None)
    #print("residual_error", residual_error)
    hist, edges = np.histogram(residual_error)
    fig.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:])
    return (fig)


ip = '127.0.0.1'
port = '12345'
socket = initialize_sub_socket(ip, port)
layout = row(generate_figure())
curdoc().add_periodic_callback(update, 1)
curdoc().add_root(layout)
