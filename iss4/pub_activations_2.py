import zmq
import pickle
import time
import numpy as np
import random

def instantiate_zmq_publisher(port=12345):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" %port)
    print('Initializing ZMQ pubstream socket')
    return(socket)


def publish_observation(initialized_socket):
    sleep_time = 0.3
    topic = b"map"
    for i in range(100):
        activation = np.random.uniform(0,1)
        pickled_contents = pickle.dumps(activation)
        #print "pickled_contents",pickled_contents, type(pickled_contents)
        try:
            initialized_socket.send_multipart([topic, pickled_contents])
            time.sleep(sleep_time)
        except Exception:
            print('Issue in publish_observation')

init_socket = instantiate_zmq_publisher()
publish_observation(init_socket)
