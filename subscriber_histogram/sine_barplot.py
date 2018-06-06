from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import Figure
from bokeh.layouts import gridplot
import numpy as np

source = ColumnDataSource(dict(x=[], y=[], avg=[]))

fig1 = Figure()
fig1.line(x='x', y='y', source=source, line_width=2, alpha=0.85, color='red')
fig1.line(x='x', y='avg', source=source, line_width=2, alpha=0.85, color='blue')
#fig2.patch('x', 'y', color='green', alpha=0.6, line_color="black", source=source)
#fig2.patch('x', 'avg', color='yellow', alpha=0.6, line_color="black", source=source)

ctr = 0
sine_sum = 0
def update_data():
    #print "update"
    global ctr, sine_sum
    ctr += 1
    sine = np.sin(ctr)
    sine_sum += sine
    new_data = dict(x=[ctr], y=[sine], avg=[sine_sum/ctr])
    source.stream(new_data, 100)
    fig1.vbar(x=ctr, top=sine, color='red', width=0.9, alpha=0.2)
    fig1.vbar(x=ctr, top=sine_sum/ctr, color='blue', width=0.9, alpha=0.6)


curdoc().add_root(fig1)
curdoc().add_periodic_callback(update_data, 100)
