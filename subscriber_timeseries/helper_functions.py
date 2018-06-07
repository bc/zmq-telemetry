import zmq
import pickle
import time

def make_clean_exit(socket_sub):
    while not socket_sub.closed:
        print("close the socket!")
        socket_sub.close()

        
def initialize_sub_socket(ip, port_sub, topic_filter=b"map"):
    context = zmq.Context()
    socket_sub = context.socket(zmq.SUB)
    socket_string = "%s:%s" % (ip, port_sub)
    print("Connecting to %s" % socket_string)
    # you can run this multiple times to receive from multiple ports
    socket_sub.connect("tcp://%s:%s" % (ip, port_sub))
    socket_sub.setsockopt(zmq.SUBSCRIBE, topic_filter)
    print('Set ZMQ Subscriber with topic filter')
    return(socket_sub)


def compose_column_data_source_entry(message_data):
    """
    extract commands via commands = message_data[0][2].
    Currently they are not used.
    """
    measuredForces = message_data[0][0]
    referenceForces = message_data[0][1]
    timestamp = message_data[1]
    print("%s" % (str(time.time() - timestamp)))
    # TODO create a function that returns measured and ref Forces in proper fmt
    new_data = dict(time=[timestamp], measured_M0=[measuredForces[0]], measured_M1=[measuredForces[1]], measured_M2=[measuredForces[2]], measured_M3=[measuredForces[3]], measured_M4=[measuredForces[4]], measured_M5=[measuredForces[0]], measured_M6=[
        measuredForces[6]], reference_M0=[referenceForces[0]], reference_M1=[referenceForces[1]], reference_M2=[referenceForces[2]], reference_M3=[referenceForces[3]], reference_M4=[referenceForces[4]], reference_M5=[referenceForces[5]], reference_M6=[referenceForces[6]])
    return(new_data)


def poll_via_zmq_socket_subscriber(socket_sub, poller):
    poller.register(socket_sub, zmq.POLLIN)
    socks = dict(poller.poll())
    if socket_sub in socks and socks[socket_sub] == zmq.POLLIN:
        [topic, msg] = socket_sub.recv_multipart()
        message = (pickle.loads(msg, encoding="latin1"))
        new_data = compose_column_data_source_entry(message)
        return(new_data)
