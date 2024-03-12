# -*- coding: utf-8 -*-
# "Loading of calcium events to Python environment and example analysis in Elephant package"

import matplotlib.pyplot as plt
import matplotlib
import os
import numpy as np
import quantities as pq
from quantities import ms, s, Hz
import neo
import elephant
import viziphant
from elephant.spike_train_synchrony import spike_contrast
from elephant.statistics import mean_firing_rate
from neo.core import SpikeTrain
import pandas as pd
from elephant import statistics
from elephant.cubic import cubic

#read calcium events
exp='example1_celena_raster.txt'
path='d:\\my_scripts\\py\\calcium\\2024\\'
os.chdir(path)
files=os.listdir('.')

#open events to array 
events=[] #read neuron events to spec
f = open(exp, 'r')
st=f.read()
events = pd.read_csv(exp,sep=' ',header=None)
f.close()
events=events[1:] #removing indexes

#removing empty channels
events_list=list() #converting events from dataframe to list
for i in range(len(events)):
    if pd.isna(events.iloc[i,0]): events_list.append(i)
events=events.drop(events_list)

events_list=list() #converting to spiketrains
for i in range(len(events)):
    events_list.append(events.iloc[i, :].dropna().tolist())
   
#converting bin to ms
sampling_rate=13.6 #fps for Celena X example data
for ite in range(len(events_list)) :
    for i in range(len(events_list[ite])):
        events_list[ite][i]=events_list[ite][i]/sampling_rate
   
spiketrains=list()
for ite in range(len(events_list)) :
    spiketrains.append(SpikeTrain(events_list[ite]*s, t_stop=5000/sampling_rate, sampling_rate=sampling_rate, sampling_period=75*ms))    

#showing raster plot
plt.figure(dpi=600)
plt.figure(figsize=(20,12))
plt.eventplot([st.magnitude for st in spiketrains], linelengths=0.75, linewidths=1.75, color='black')
plt.xlabel("Time, s")
plt.ylabel("Channels")
plt.show()

#firing rate
frate=[]
for it in range(len(spiketrains)):
    frate.append(mean_firing_rate(SpikeTrain(spiketrains[it], t_stop=300*s), t_start=0*s, t_stop=300*s))
print(np.mean(frate))


#Spike-contrast synchrony for all range https://elephant.readthedocs.io/en/stable/reference/_toctree/spike_train_synchrony/elephant.spike_train_synchrony.spike_contrast.html
round(elephant.spike_train_synchrony.spike_contrast(spiketrains, t_start=0*s, t_stop=300*s, min_bin=1 * s, bin_shrink_factor=0.9, return_trace=False),3)

#CuBIC https://elephant.readthedocs.io/en/latest/reference/cubic.html
pop_count = statistics.time_histogram(spiketrains, bin_size=1 * s)
plt.hist(pop_count)
xi, p_val, kappa, test_aborted = cubic(pop_count, alpha=0.05)
print(xi, p_val)

#SPADE https://elephant.readthedocs.io/en/latest/reference/spade.html
binn=20 #main SPADE parameter bin size, s
patterns = elephant.spade.spade(
    spiketrains=spiketrains, binsize=binn*pq.s, winlen=1, min_spikes=2, 
    n_surr=100,dither=5*pq.ms,
    psr_param=[0,0,0],
    output_format='patterns')['patterns']
patterns[0:10]
plt.figure(dpi=600)
plt.figure(figsize=(40,24))
viziphant.spade.plot_patterns(spiketrains, patterns,circle_sizes=(5,15,15))
plt.savefig('foo.svg', bbox_inches='tight')
plt.show()
