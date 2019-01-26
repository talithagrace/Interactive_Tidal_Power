from bokeh.plotting import figure, curdoc, output_file
from bokeh.io import push_notebook, output_notebook, show
from bokeh.layouts import column, row, widgetbox
from bokeh.models import Slider, ColumnDataSource, Div, Select
import numpy as np
import math
from numpy import vectorize

d = 1000 #density of water kg/m3
g = 9.81 #gravitational acceleration m2/s
k_s = 0 #sluice hydraulic loss
k_t = 0.02 #turbine hydraulic loss
dt = 720 #change in time s
Cd_s = 0.6 #sluice discharge coefficient when open, 0 when closed
Cd_t = 0.975 #turbine discharge coefficient when off
Qt = 4.4 #specific discharge turbine when on m3/s
w = (2 * math.pi) / 12.4 #angular frequency / no. of radians sine wave goes through per unit of time 12.4 hr cycle
dx = 0
n_t = 0.9
n_g = 0.95
D_t = 5 #turbine diameter meters
sluice_area = 10 #area of one sluice in m2
r = D_t / 2
no_turbines = 30
A_t = no_turbines * (math.pi * r**2) #area of turbine
A_l = 95000000 #area of lagoon m2
no_sluices = 20
A_s = no_sluices * sluice_area #total sluice area
time = np.linspace(0, 49.6, num=249) #start, stop, number of increments to give intervals of 0.2
h_tide = 5.5 + 3.25 * np.sin(w * (time - 9.25))
h_lagoon = 0 #estimate height at start of tide
x = time
y1 = h_tide


for i in range(len(time)):
    if ((i >= 0 and i <= 2.4) or (i >= 9.4 and i <=13.6) or (i >= 22.2 and i <= 25.6) or (i >= 34.2 and i <= 38) or (i >= 46.6 and i <= 49.6)):
        h = h_tide - h_lagoon
        h_net = h * (1 - k_t)
        Q = np.sqrt(abs(2 * g * h_net)) * A_t * Qt #flow rate through turbine
        dx = (Q / A_l) * dt #change in lagoon height
        h_lagoon = h_lagoon + dx
        y2 = h_lagoon
        for height in h_net:
            y3 = (d*g*h_net*n_t*n_g*Q)/1000000
    else:
        h = h_tide - h_lagoon
        h_net = h * (1 - k_s)
        Q_s = np.sqrt(abs(2 * g * h_net)) * A_s * Cd_s #flow rate through sluice
        #Q = np.sqrt(abs(2 * g * h_net)) * A_t * Qt #flow rate through turbine
        dx = (Q_s / A_l) * dt #change in lagoon height
        h_lagoon = h_lagoon + dx
        y2 = h_lagoon
        #for height in h_net:
        #    y3 = (d*g*h_net*n_t*n_g*Q_s)/1000000



source = ColumnDataSource(data=dict(x=x, y1=y1, y2=y2, y3=y3))

p = figure(width=900, height=400, y_range=(2,10), x_axis_label="time(hrs)", y_axis_label="height(m)")
p.circle(x='x', y='y1', source=source, size=7, color="firebrick", alpha=0.5, legend="tide height")
p.circle(x='x', y='y2', source=source, size=7, color="blue", alpha=0.5, legend="lagoon height")
p.legend.location = "top_left"
p1 = figure(width=900, height=400, x_range=(0, 50), y_range=(0,1200), x_axis_label="time(hrs)", y_axis_label="power(MW)")
p1.circle(x='x', y='y3', source=source, size=7, color="firebrick", alpha=0.5, legend="power(MW)")

sluices = Slider(title="number of sluices", value=20, start=5, end=40, step=1)
turbines = Slider(title="number of turbines", value=30, start=20, end=50, step=2)
lagoon  = Slider(title ="lagoon area(m2)", value=90000000, start=85000000, end=95000000, step=10000)
#choice = Select(title="Generation Mode:", value="0", options=[(0*np.sqrt(abs(2 * g * h_net)) * A_s * Cd_s), (np.sqrt(abs(2 * g * h_net)) * A_s * Cd_s)])

def update_data(attrname, old, new):

    #get the current slider values
    #Q_2 = choice.value
    no_sluices = sluices.value
    no_turbines = turbines.value
    A_l = lagoon.value
    A_t = no_turbines * (math.pi * r**2) #area of turbine
    sluice_area = 10 #area of one sluice in m2
    A_s = no_sluices * sluice_area #total sluice area

    #generate the new curve
    h_lagoon = 0
    x = time
    y1 = h_tide

    for i in range(len(time)):
        if ((i >= 0 and i <= 2.4) or (i >= 9.4 and i <=13.6) or (i >= 22.2 and i <= 25.6) or (i >= 34.2 and i <= 38) or (i >= 46.6 and i <= 49.6)):
            h = h_tide - h_lagoon
            h_net = h * (1 - k_t)
            Q = np.sqrt(abs(2 * g * h_net)) * A_t * Qt #flow rate through turbine
            dx = (Q / A_l) * dt #change in lagoon height
            h_lagoon = h_lagoon + dx
            y2 = h_lagoon

            for height in h_net:
                y3 = (d*g*h_net*n_t*n_g*Q)/1000000
        else:
            h = h_tide - h_lagoon
            h_net = h * (1 - k_s)
            Q_s = np.sqrt(abs(2 * g * h_net)) * A_s * Cd_s #flow rate through sluice
            #Q = np.sqrt(abs(2 * g * h_net)) * A_t * Qt #flow rate through turbine
            #Q_2 = 0
            dx = (Q_s / A_l) * dt #change in lagoon height
            h_lagoon = h_lagoon + dx
            y2 = h_lagoon
            #for height in h_net:
            #    y3 = (d*g*h_net*n_t*n_g*Q_s)/1000000


    source.data = dict(x=x, y1=y1, y2=y2, y3=y3)


for w in [sluices, turbines, lagoon]:
    w.on_change('value', update_data)

#set up layouts and add to document
title = Div(text="<h2>Tidal power generation in the Severn Estuary</h2>")
guide = Div(text="<h3>Move the sliders to change the number of turbines, sluices and the area of the lagoon. Power is generated as the lagoon fills up and the water passes through the turbines</h3>")
inputs = widgetbox(sluices, turbines, lagoon)

#curdoc().add_root(column(inputs, p, p1))
curdoc().add_root(row((column(title, guide, inputs)),(column(p, p1))))
