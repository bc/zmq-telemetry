from bokeh.layouts import column, layout
import time
import pdb
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Range1d
from bokeh.plotting import Figure
import numpy as np
import sys
from sub import initialize_sub_socket, receive_and_depickle


def create_figline(muscle_index):
    global fig, source
    colors = ["#762a83",
    "#af8dc3",
    "#e7d4e8",
    "#000000",
    "#d9f0d3",
    "#7fbf7b",
    "#1b7837"]
    fig.line(source=source, x='timestamp', y='measured_M%s' %
    muscle_index, line_width=2, alpha=0.85,
    color=colors[muscle_index])


  ip = "169.254.12.240"
  port = "12345"

  if len(sys.argv) > 1:
    ip = sys.argv[1]

    if len(sys.argv) > 2:
      port = sys.argv[2]

      source = ColumnDataSource(dict(timestamp=[],
       measured_M0=[],
       measured_M1=[],
       measured_M2=[],
       measured_M3=[],
       measured_M4=[],
       measured_M5=[],
       measured_M6=[],
       command_M0=[],
       command_M1=[],
       command_M2=[],
       command_M3=[],
       command_M4=[],
       command_M5=[],
       command_M6=[]))

      fig = Figure(plot_width=1800, plot_height=400)
      [create_figline(i) for i in range(7)]

      fig.y_range = Range1d(-0.5, 3.5)
      ct = 0

      def signal_to_tuple_entries(forces, prefix):
        return([("%s%s" % (prefix, str(i)), [forces[i]]) for i in range(len(forces))])

        start = time.time()

        def sine_updater():
          global ct, socket, start
  # pdb.set_trace()
  # forces,targetforces,commands
  [values, timestamp] = receive_and_depickle(socket)
  most_recent_timestamp = timestamp
  [forces, targetforces, commands] = values
  force_dictionary = dict([("timestamp", [timestamp])] +
      signal_to_tuple_entries(forces, "measured_M") +
      signal_to_tuple_entries(commands, "command_M")
      )
  # print(message)
  ct += 1
  new_data = force_dictionary
  # pdb.set_trace()
  source.stream(new_data, 80)
  if ct % 100 == 0:
    elapsed_time = time.time() - start
    amortized_rate = ct / elapsed_time
    print("Msg: %s |Messages per second: %s" % (ct, str(amortized_rate)))
    # flush the amortized rate buffer every 5 seconds
    if elapsed_time > 5:
      start = time.time()
      ct = 0


fig2 = fig  # make copy
socket = initialize_sub_socket(ip, port)
dash_layout = layout([[fig], [fig2]], sizing_mode='stretch_both')
curdoc().add_root(dash_layout)
curdoc().add_periodic_callback(sine_updater, 0.1)
