import numpy as np
import zmq
import pickle
import sys



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


def update_data(socket):
    while True:
        [topic, msg] = socket.recv_multipart()
        message = pickle.loads(msg, encoding="latin1")
        print("MESSAGE", message)
        if message == "Continue":
            pass
        else:
            sys.exit()


ip = '127.0.0.1'
port = '12345'
socket = initialize_sub_socket(ip, port)
update_data(socket)
