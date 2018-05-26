import bokeh
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import Figure
from bokeh.models.widgets import RadioGroup
from bokeh.layouts import row
import numpy as np
import time
import zmq
import pdb; #pdb.set_trace()

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt_string(zmq.SUBSCRIBE,'')
socket.connect('tcp://127.0.0.1:1234')

source = ColumnDataSource(dict(x=[], y=[], avg=[]))
radio_group = RadioGroup(labels=["50", "100", "200", "500", "1000"], active=0)
rollback_lt = 50

def change_lt():
    global radio_group,rollback_lt
    vals = [50,100,200,500,1000]
    ind = radio_group.active
    rollback_lt = vals[ind]

radio_group.on_change('active', lambda attr, old, new: change_lt())

timer_cnt = 0
def update_data():
    global timer_cnt, stream, rollback_lt
    timer_cnt += 1
    start = time.time()
    string = socket.recv()
    x, y, avg = string.split()
    x = int(x); y = float(y); avg = float(avg)
    #print(x, y, avg)
    new_data = dict(x=[x], y=[y], avg=[avg])
    source.stream(new_data,rollback_lt)
    #print(source.data['x'], len(source.data['x']))
    if timer_cnt%50 == 0:
        print("elapsed time = ", time.time()-start)

def update():
    layout.children[0] = generate_figure()

def generate_figure():
    global source
    fig2 = Figure()
    update_data()
    hist, edges = np.histogram(source.data['y'])
    #print("x,y,avg", source.data['x'], source.data['y'], source.data['avg'])
    #print("hist",hist)
    fig2.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:])
    return (fig2)

#print("radio_button_group", radio_group)
layout = row(generate_figure(), radio_group)
curdoc().add_periodic_callback(update, 1)
curdoc().add_root(layout)
