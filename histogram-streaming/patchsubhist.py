import bokeh
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import Figure
from bokeh.layouts import row
from bokeh.plotting import reset_output
import numpy as np
import time
import zmq
import pdb; #pdb.set_trace()

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt_string(zmq.SUBSCRIBE,'')
socket.connect('tcp://127.0.0.1:1234')

source = ColumnDataSource(dict(x=[], y=[], avg=[]))

#fig1 = Figure()
#fig1.line(x='x', y='y', source=source, line_width=2, alpha=0.85, color='red')
#fig1.line(x='x', y='avg', source=source, line_width=2, alpha=0.85, color='blue')
fig2 = Figure()

timer_cnt = 0
index = 0
first_time = True
def update_data():
    global timer_cnt, index, first_time
    timer_cnt += 1
    start = time.time()
    string = socket.recv()
    x, y, avg = string.split()
    #pdb.set_trace()
    x = int(x); y = float(y); avg = float(avg)
    #print(x, y, avg)
    new_data = dict(x=[x], y=[y], avg=[avg])
    if index < 10 and first_time:
        source.stream(new_data)
        #print(index)
    else:
        source.patch(dict(x=[(index,x)], y=[(index,y)], avg=[(index,avg)]))
    #pdb.set_trace()
    hist, edges = np.histogram(source.data['y'])
    #print(hist)
    fig2.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:])
    if timer_cnt%50 == 0:
        print("elapsed time = ", time.time()-start)
    index += 1
    if index == 10:
        index = 0
        first_time = False



#p = row(fig1,fig2)
curdoc().add_periodic_callback(update_data, 1)
curdoc().add_root(fig2)
