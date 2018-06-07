
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