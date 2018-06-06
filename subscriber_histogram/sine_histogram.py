from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import Figure
from bokeh.layouts import gridplot
import numpy as np
import time
import cProfile
import re


ctr = 0
sine_sum = 0

source = ColumnDataSource(dict(x=[], y=[], avg=[]))

fig1 = Figure()
fig1.line(x='x', y='y', source=source, line_width=2, alpha=0.85, color='red')
fig1.line(x='x', y='avg', source=source, line_width=2, alpha=0.85, color='blue')
fig2 = Figure()
print "X, Sine Y values", source.data['x'],source.data['y']
# hist, edges = np.histogram(source.data['y'])
# fig2.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:])

#timer_cnt = 0
def update_data():
    #start = time.time()
    #timer_cnt += 1
    #print "update"
    global ctr, sine_sum
    ctr += 1
    #rand = np.random.uniform(-1, 1)
    sine = np.sin(ctr)
    sine_sum += sine
    new_data = dict(x=[ctr], y=[sine], avg=[sine_sum/ctr])
    source.stream(new_data, 100)
    #fig1.vbar(x=ctr, top=sine, color='red', width=0.9, alpha=0.2)
    #fig1.vbar(x=ctr, top=sine_sum/ctr, color='blue', width=0.9, alpha=0.6)
    hist, edges = np.histogram(source.data['y'])
    fig2.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:])
    #hist = Histogram(x)
    #elapsed_time = time.time() - start


#print 'ex', x, type(x)
p = gridplot([[fig1,fig2]])
curdoc().add_periodic_callback(update_data, 1)
curdoc().add_root(p)

#cProfile.run(re.compile("curdoc().add_periodic_callback(update_data, 1)"))
