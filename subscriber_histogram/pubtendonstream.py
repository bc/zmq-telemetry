import zmq
import pickle
import time
import numpy as np
import random

def instantiate_zmq_publisher(port=12345):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:%s" %port)
    print('Initializing ZMQ pubstream socket')
    return(socket)

sample_data = np.random.uniform(0.0, 10.0, 100)

def publish_observation(initialized_socket, messagedata):
    topic = b"map"
    while True:
        measuredForces = []
        targetForces = []
        commands = []
        measuredForces.append([random.uniform(0,1) for i in range(7)])
        targetForces.append([random.uniform(0,1) for i in range(7)])
        commands.append([random.uniform(1,500) for i in range(7)])
        messagedata = (np.vstack([measuredForces, targetForces, commands]), time.time())
        #print messagedata #print messagedata[0][0]
        #print("%d %d" % (topic, messagedata[0]))
        pickled_contents = pickle.dumps(messagedata)
        #print "pickled_contents",pickled_contents, type(pickled_contents)

        try:
            initialized_socket.send_multipart([topic, pickled_contents])
            time.sleep(0.1)
        except Exception:
            print('Issue in publish_observation')

measuredForces = [  -0.002,   -0.067,    0.012,    0.468,    0.004,    0.173, 0.018]
targetForces = [   0.5  ,    0.5  ,    0.5  ,    0.5  ,    0.5  ,    0.5  ,    0.5  ]
commands = [ 501.505,  567.134,  487.761,   32.315,  495.827,  327.038, 482.083]

observation = (np.vstack([measuredForces, targetForces, commands]), time.time())

init_socket = instantiate_zmq_publisher()
publish_observation(init_socket, observation)
