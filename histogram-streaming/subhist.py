import bokeh
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import Figure
from bokeh.models.widgets import TextInput
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

fig1 = Figure()
fig1.line(x='x', y='y', source=source, line_width=2, alpha=0.85, color='red')
fig1.line(x='x', y='avg', source=source, line_width=2, alpha=0.85, color='blue')
fig2 = Figure()
text_input = TextInput(value='10', title="Label:")
timer_cnt = 0
patch_flag = True
index = 0
def update_data():
    global timer_cnt, index, patch_flag
    timer_cnt += 1
    start = time.time()
    string = socket.recv()
    x, y, avg = string.split()
    x = int(x); y = float(y); avg = float(avg)
    #print(x, y, avg)
    new_data = dict(x=[x], y=[y], avg=[avg])
    source.stream(new_data,10)
    #pdb.set_trace()
    hist, edges = np.histogram(source.data['y'])
    #print("x,y,avg", source.data['x'], source.data['y'], source.data['avg'])
    #print("hist",hist)
    fig2.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:])
    if timer_cnt%50 == 0:
        print("elapsed time = ", time.time()-start)


p = row(fig1,fig2,text_input)
curdoc().add_periodic_callback(update_data, 1)
curdoc().add_root(p)
