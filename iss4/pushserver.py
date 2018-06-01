import zmq
import time
import random

def server_push(port="5556"):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.bind("tcp://*:%s" % port)
    print "Running server on port: ", port
    while True:
        referenceForce = random.uniform(0,1)
        socket.send(referenceForce)
        time.sleep (8)

server_push()
