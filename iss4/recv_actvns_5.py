from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import Figure
from bokeh.layouts import gridplot, row
import numpy as np
import time
import cProfile
import random
import zmq
import pickle

ctr = 0
sine_sum = 0

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
command_M0=[],
command_M1=[],
command_M2=[],
command_M3=[],
command_M4=[],
command_M5=[],
command_M6=[]))

fig1 = Figure()
fig1.line(x='time', y='measured_M0', source=source, line_width=2, alpha=0.85, color='red')
fig2 = Figure()
fig2.line(x='time', y='command_M1', source=source, line_width=2, alpha=0.85, color='blue')

def update_data():
    global socket
    try:
        [topic, msg] = socket.recv_multipart()
        #print("VALUES", msg)
        message = (pickle.loads(msg, encoding="latin1"))
        #print("values", message)
        #[forces, targetforces, commands] = message
        measuredForces = message[0][0]
        targetForces = message[0][1]
        commands = message[0][2]
        timestamp = message[1]
        # print("FORCES",message[0][0])
        # print("TARGETFORCES",message[0][1])
        # print("COMMANDS",message[0][2])
        # print("TIMESTAMP", message[1])
        # for i in range(7):
        #     "measured_M%s"%i = measuredForces[i]
        #     ("command_M%s"%i) = commands[i]

        new_data = dict(time=[timestamp],measured_M0=[measuredForces[0]],measured_M1=[measuredForces[1]],measured_M2=[measuredForces[2]],measured_M3=[measuredForces[3]],measured_M4=[measuredForces[4]],measured_M5=[measuredForces[0]],measured_M6=[measuredForces[6]],command_M0=[commands[0]],command_M1=[commands[1]],command_M2=[commands[2]],command_M3=[commands[3]],command_M4=[commands[4]],command_M5=[commands[5]],command_M6=[commands[6]])

        source.stream(new_data, 100)
        #print(source.data['measuredForces'])

    except KeyboardInterrupt:
        socket.close()

ip = '127.0.0.1'
port = '12345'
socket = initialize_sub_socket(ip, port)

curdoc().add_periodic_callback(update_data, 1)
curdoc().add_root(row(fig1,fig2))

#cProfile.run(re.compile("curdoc().add_periodic_callback(update_data, 1)"))
