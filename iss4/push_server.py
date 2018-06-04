import zmq
import time
import random
import pickle

def server_push(port="5556"):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % port)
    print "Running server on port: ", port
    while True:
        message = socket.recv()
        print "Received request: ", message
        referenceForces = []
        referenceForces.append([random.uniform(0,1) for i in range(7)])
        #print("Continue")
        pickled_contents = pickle.dumps(referenceForces)
        socket.send(pickled_contents)
        #msg = socket.recv()
        #print(msg)
        time.sleep(8)

server_push()
