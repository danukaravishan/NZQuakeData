## This is a stand alone script to configure the ML database required for training.


## TODO
## Make this functional
## Configure to resize the window
## Add a resampling

import h5py
import numpy as np
import obspy
from obspy import Trace
from obspy import Stream
import os
import pandas as pd
import matplotlib.pyplot as plt
import random
from scipy.signal import decimate


# Parameters 
WINDOW_DURATION   = 4
DATABASE_FILE = "/Users/user/Desktop/Temp/waveforms.hdf5"
NEW_DATABASE  = "data/waveforms_4s_full.hdf5" # Overide if file alreay exist
ORIGINAL_SAMPLING_RATE = 50 # Most of the data points are in this category. Hence choosing as the base sampling rate

def extract_wave_window(data, wave_index, window_size):
    end = wave_index + window_size
    return data[:, wave_index:end]

def extract_noise_window(data, window_size):
    return data[:, -window_size:]

def downsample(data, original_rate, target_rate):
    downsample_factor = int(target_rate // original_rate)
    return decimate(data, downsample_factor, axis=1, zero_phase=True)

def main():
    hdf5_file = h5py.File(DATABASE_FILE, 'r')
    duration = 4 # 2 seconds

    if os.path.isfile(NEW_DATABASE):
        os.remove(NEW_DATABASE)

    with h5py.File(NEW_DATABASE, 'a') as hdf:
        
        # Create database groups
        if 'positive_samples_p' not in hdf:
            positive_group_p = hdf.create_group('positive_samples_p')
        else:
            positive_group_p = hdf['positive_samples_p']

        if "positive_samples_s" not in hdf:
            positive_group_s = hdf.create_group('positive_samples_s')
        else:
            positive_group_s = hdf['positive_samples_s']

        if "negative_sample_group" not in hdf:
            negative_group = hdf.create_group('negative_sample_group')
        else:
            negative_group = hdf['negative_sample_group']

        count = 0
        downsample_factor = 1

        for event_id in hdf5_file.keys():
            print(event_id)
            dataset = hdf5_file.get(event_id)
            data = np.array(dataset)

            p_arrival_index = dataset.attrs["p_arrival_sample"]
            s_arrival_index = dataset.attrs["s_arrival_sample"]

            sampling_rate = dataset.attrs["sampling_rate"]

            if int(sampling_rate) != 50:
                # Add code to resample to 50
                print(sampling_rate) 
                data_resampled = downsample(data, ORIGINAL_SAMPLING_RATE, int(sampling_rate))
                data = data_resampled
                downsample_factor = int(sampling_rate // ORIGINAL_SAMPLING_RATE)
                p_arrival_index = int(int(p_arrival_index)/downsample_factor)
                s_arrival_index = int(int(s_arrival_index)/downsample_factor)
                sampling_rate = ORIGINAL_SAMPLING_RATE
            
            count +=1
            window_size = WINDOW_DURATION * sampling_rate
            p_data  = extract_wave_window(data, int(p_arrival_index), int(window_size))
            s_data = extract_wave_window(data, int(s_arrival_index), int(window_size))
            noise_data = extract_noise_window(data, int(window_size))
            

            ## Add data to each groups
            if event_id not in positive_group_p:
                positive_p_dataset = positive_group_p.create_dataset(event_id, data=p_data)
            else:
                print(f"Dataset {event_id} already exists in positive_samples_p. Skipping.")

            if event_id not in positive_group_s:
                positive_s_dataset = positive_group_s.create_dataset(event_id, data=s_data)
            else:
                print(f"Dataset {event_id} already exists in positive_samples_s. Skipping.")

            if event_id not in negative_group:
                negative_dataset = negative_group.create_dataset(event_id, data=noise_data)
            else:
                print(f"Dataset {event_id} already exists in negative_group. Skipping.")

            for key, value in dataset.attrs.items():
                positive_group_p[event_id].attrs[key] = value
                positive_group_s[event_id].attrs[key] = value
                negative_group[event_id].attrs[key] = value

    print ("Number of records " + str(count))

if __name__ == "__main__":
    main()