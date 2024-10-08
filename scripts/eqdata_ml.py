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
import seisbench.models as sbm
import time
import tensorflow as tf

DEFINE_NO_PLOT = False


def numpy_to_stream(data, channel):

    # Additional information (optional)
    sampling_rate = data.attrs["sampling_rate"]  # Hz
    station_id = data.attrs["station_id"]
    network_code = data.attrs["network_code"]
    channel_code = data.attrs["channel_code"]+channel  # Append Z,N,E acordingly 0-> Z, 1->N, 2->E
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
waveforms_path = database_dir + "\waveforms_new.hdf5"

df = pd.read_csv(metadata_path)

ev_list = df['Earthquake Key'].to_list()
dtfl = h5py.File(waveforms_path, 'r')

model = sbm.EQTransformer.from_pretrained("original")
print(model.weights_docstring)

time_count = 1
average_time = 0
total_time = 0

# Here use the list of earthquakes that has happened from 2013 - 2022
for c, evi in enumerate(ev_list):
    dataset = dtfl.get(evi) 
    if dataset == None :
        continue
    
    data = np.array(dataset)
    
    st_z = numpy_to_stream(dataset, "Z")
    st_n = numpy_to_stream(dataset, "N")
    st_e = numpy_to_stream(dataset, "E")

    stream = Stream()
    
    for st in [st_z, st_n, st_e]:
        for trace in st:
            stream.append(trace)
    
    begin = time.time() 
    annotations = model.annotate(stream)
    end = time.time() 
    annotate_time = end - begin

    print("Annotation numer : "+str(time_count))
    print("Earthquake ID : " +str(evi))
    print(f"\nRuntime of the annotation = {annotate_time} seconds")

    total_time += annotate_time
    average_time = total_time/time_count    
    time_count+=1

    print(f"Average time for one annotation = {average_time} seconds")

    print(annotations)

    if(annotations.count() <= 0):
        print("Not detected\n")
        continue
    
    if DEFINE_NO_PLOT:
        continue

    fig = plt.figure(figsize=(15, 10))
    axs = fig.subplots(2, 1, sharex=True, gridspec_kw={'hspace': 0})
    
    axs[0].set_title("Event ID : "+str(evi))

    offset = annotations[0].stats.starttime - stream[0].stats.starttime
    
    for i in range(3):
        axs[0].plot(stream[i].times(), stream[i].data, label=stream[i].stats.channel)
        if annotations[i].stats.channel[-1] != "N":  # Do not plot noise curve
            axs[1].plot(annotations[i].times() + offset, annotations[i].data, label=annotations[i].stats.channel)

    axs[0].legend()
    axs[1].legend()
    
    plt.show()

    inp = input("Press a key to plot the next waveform!")
    if inp == "r":
        continue
