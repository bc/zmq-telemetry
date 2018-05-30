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
reference_M0=[],
reference_M1=[],
reference_M2=[],
reference_M3=[],
reference_M4=[],
reference_M5=[],
reference_M6=[]))

fig1 = figure()
#fig1.multi_line(xs=[[time],[time]], ys=[[measured_M0], [command_M0]], source=source, line_width=2, alpha=0.85, color=['red','blue'])
# fig2 = Figure()
# fig2.line(x='time', y='command_M1', source=source, line_width=2, alpha=0.85, color='blue')
fig1.line(x='time', y='measured_M0', source=source, line_width=2, alpha=0.85, color='red')
fig1.line(x='time', y='reference_M0', source=source, line_width=2, alpha=0.85, color='blue')


def update_data():
    global socket
    try:
        [topic, msg] = socket.recv_multipart()
        #print("VALUES", msg)
        message = (pickle.loads(msg, encoding="latin1"))
        #print("values", message)
        #[forces, targetforces, commands] = message
        measuredForces = message[0][0]
        referenceForces = message[0][1]
        #residualForces = [message[0][0][i]-message[0][1][i] for i in range(7)]
        commands = message[0][2]
        timestamp = message[1]
        # print("FORCES",message[0][0])
        # print("TARGETFORCES",message[0][1])
        # print("COMMANDS",message[0][2])
        # print("TIMESTAMP", message[1])
        # for i in range(7):
        #     "measured_M%s"%i = measuredForces[i]
        #     ("command_M%s"%i) = commands[i]

        new_data = dict(time=[timestamp],measured_M0=[measuredForces[0]],measured_M1=[measuredForces[1]],measured_M2=[measuredForces[2]],measured_M3=[measuredForces[3]],measured_M4=[measuredForces[4]],measured_M5=[measuredForces[0]],measured_M6=[measuredForces[6]],reference_M0=[referenceForces[0]],reference_M1=[referenceForces[1]],reference_M2=[referenceForces[2]],reference_M3=[referenceForces[3]],reference_M4=[referenceForces[4]],reference_M5=[referenceForces[5]],reference_M6=[referenceForces[6]])

        source.stream(new_data, 100)
        #print(source.data['measuredForces'])

    except KeyboardInterrupt:
        socket.close()

ip = '127.0.0.1'
port = '12345'
socket = initialize_sub_socket(ip, port)

curdoc().add_periodic_callback(update_data, 1)
curdoc().add_root(fig1)

#cProfile.run(re.compile("curdoc().add_periodic_callback(update_data, 1)"))
