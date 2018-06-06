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

k = 0
def publish_observation(initialized_socket):
    sleep_time = 1
    topic = b"map"
    while True:
        global k
        k = k+1
        measuredForces = []
        referenceForces = []
        commands = []
        measuredForces.append([random.uniform(0,1) for i in range(7)])
        referenceForces.append([0.5 for i in range(7)])
        commands.append([random.uniform(1,500) for i in range(7)])
        messagedata = (np.vstack([measuredForces, referenceForces, commands]), time.time())
        pickled_contents = pickle.dumps(messagedata)
        #print "pickled_contents: ",pickled_contents, type(pickled_contents)

        try:
            initialized_socket.send_multipart([topic, pickled_contents])
            print(k)
            time.sleep(sleep_time)
        except Exception:
            print('Issue in publish_observation')

init_socket = instantiate_zmq_publisher()
publish_observation(init_socket)
