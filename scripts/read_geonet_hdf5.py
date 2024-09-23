import pandas as pd
import h5py
import numpy as np
import matplotlib.pyplot as plt
import os
import seisbench.data as sbd
import seisbench.util as sbu
from seisbench.data import WaveformDataset
import obspy
from obspy import Trace
from obspy import Stream

def numpy_to_stream(data):

    # Additional information (optional)
    sampling_rate = data.attrs["sampling_rate"]  # Hz
    station_id = data.attrs["station_id"]
    network_code = data.attrs["network_code"]
    channel_code = data.attrs["channel_code"]+"Z"  # Append Z,N,E acordingly 0-> Z, 1->N, 2->E
    start_time   = obspy.core.utcdatetime.UTCDateTime(data.attrs["stream_starttime"]) 

    npdata = np.array(data)

    trace = Trace(data=npdata[0,:], 
                header={"sampling_rate": sampling_rate,
                        "station": station_id,
                        "network": network_code,
                        "channel": channel_code,
                        "starttime": start_time})

    stream = Stream([trace])
    return stream

# Open the HDF5 file
base_path = os.getcwd()
database_dir = base_path + "\data"
metadata_path = database_dir + "\metadata.csv"
waveforms_path = database_dir + "\waveforms.hdf5"

df = pd.read_csv(metadata_path)

ev_list = df['Earthquake Key'].to_list()
dtfl = h5py.File("data\waveforms.hdf5", 'r')

for c, evi in enumerate(ev_list):
    dataset = dtfl.get(evi) 
    if dataset == None :
        continue
    
    data = np.array(dataset)
    
    fig = plt.figure()
    ax = fig.add_subplot(311)
    plt.plot(data[0,:], 'k')
    plt.rcParams["figure.figsize"] = (8, 5)
    legend_properties = {'weight':'bold'}    
    plt.tight_layout()
    ymin, ymax = ax.get_ylim()
    pl = plt.vlines(dataset.attrs['p_arrival_sample'], ymin, ymax, color='b', linewidth=3, label='P-arrival')
    sl = plt.vlines(dataset.attrs['s_arrival_sample'], ymin, ymax, color='r', linewidth=3, label='S-arrival')
    plt.legend(handles=[pl, sl], loc = 'upper right', borderaxespad=0., prop=legend_properties)        
    plt.ylabel('Accelaration: Z (m/s/s)', fontsize=12) 
    ax.set_xticklabels([])

    ax = fig.add_subplot(312)         
    plt.plot(data[1,:], 'k')
    plt.rcParams["figure.figsize"] = (8, 5)
    legend_properties = {'weight':'bold'}    
    plt.tight_layout()
    ymin, ymax = ax.get_ylim()
    pl = plt.vlines(dataset.attrs['p_arrival_sample'], ymin, ymax, color='b', linewidth=3, label='P-arrival')
    sl = plt.vlines(dataset.attrs['s_arrival_sample'], ymin, ymax, color='r', linewidth=3, label='S-arrival')
    plt.legend(handles=[pl, sl], loc = 'upper right', borderaxespad=0., prop=legend_properties)        
    plt.ylabel('Accelaration: N (m/s/s)', fontsize=12) 
    ax.set_xticklabels([])

    ax = fig.add_subplot(313)         
    plt.plot(data[2,:], 'k')
    plt.rcParams["figure.figsize"] = (8,5)
    legend_properties = {'weight':'bold'}    
    plt.tight_layout()
    ymin, ymax = ax.get_ylim()
    pl = plt.vlines(dataset.attrs['p_arrival_sample'], ymin, ymax, color='b', linewidth=3, label='P-arrival')
    sl = plt.vlines(dataset.attrs['s_arrival_sample'], ymin, ymax, color='r', linewidth=3, label='S-arrival')
    plt.legend(handles=[pl, sl], loc = 'upper right', borderaxespad=0., prop=legend_properties)        
    plt.ylabel('Accelaration: E (m/s/s)', fontsize=12) 
    ax.set_xticklabels([])
    plt.show() 

    for at in dataset.attrs:
        print(at, dataset.attrs[at])    

    inp = input("Press a key to plot the next waveform!")
    if inp == "r":
        continue 