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
    #sample_data = np.random.uniform(0.0, 10.0, 100)
    topic = b"map"
    for i in range(10):
        if i < 6:
            sample_data = "Continue"
        else:
            sample_data = "Exit"
        pickled_contents = pickle.dumps(sample_data)
        #print "pickled_contents",pickled_contents, type(pickled_contents)
        try:
            initialized_socket.send_multipart([topic, pickled_contents])
            time.sleep(0.2)
        except Exception:
            print('Issue in publish_observation')

init_socket = instantiate_zmq_publisher()
publish_observation(init_socket)
