# How to run the bokeh server with python3

###### Instructions to run a Local Pi Emulator
Run 'python3 pubActivations.py' on terminal  
Run 'bokeh serve --show subPlotActivations.py' on another terminal  
Run 'bokeh serve --port 5001 --show HistResidualForces.py' on yet another terminal  

###### Instructions to run on Pi
In 'subPlotActivations.py', set 'rpi_emulator' to False  
Change user_variable to True or False accordingly [ex: 'brian=False' on sithara's machine]  

[pubstream from main.py must be running on Rpi]  
Run 'bokeh serve --show subPlotActivations.py' on terminal in local machine  
Run 'bokeh serve --port 5001 --show HistResidualForces.py' on yet another terminal  


```bash
/anaconda/bin/python3 /usr/local/bin/bokeh serve --show recv_actns.py
```
