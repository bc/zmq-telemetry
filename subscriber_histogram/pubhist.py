import zmq
import time
import numpy as np

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://127.0.0.1:1234')

ctr = 0
sine_sum = 0
while True:
    global ctr,sine_sum
    ctr += 1
    sine = np.sin(ctr)
    sine_sum += sine
    #print "%d %f %f" % (ctr, sine, sine_sum/ctr)
    socket.send("%d %f %f" % (ctr, sine, sine_sum/ctr))
    time.sleep(0.1)
