import zmq
import time
import random
import pickle

def server_push(port="5556"):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.bind("tcp://*:%s" % port)
    print "Running server on port: ", port
    while True:
        referenceForces = []
        referenceForces.append([random.uniform(0,1) for i in range(7)])
        #print("Continue")
        pickled_contents = pickle.dumps(referenceForces)
        socket.send(pickled_contents)
        time.sleep(8)

server_push()

#### once the fig starts being plotted on the browser, PULLING vanishes only PUBBING is there ###
