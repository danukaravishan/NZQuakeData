import pandas as pd
import h5py
import os
import pandas as pd
import obspy
from obspy import UTCDateTime
import numpy as np

## Main class for handling seismic database
class DatabaseWriter:
    def __init__(self, hdf_file):
        self.hdf_file = hdf_file
        self.buckets = {}
        self.events = []

        if (os.path.exists(hdf_file)):
            print(f"File not found %s",hdf_file)
                                      
    def save_event_to_hdf(self, event):
        with h5py.File(self.hdf_file, 'a') as hdf:
            for waveform in event.waveforms:    
                try:
                    d = hdf.create_dataset(waveform.wave_id, data=waveform.data)
                    d.attrs["station_id"] = waveform.station_id
                    d.attrs["magnitude"] = event.magnitude
                    d.attrs["p_wave_picktime"] = waveform.p_wave_picktime
                    d.attrs["s_wave_picktime"] = waveform.s_wave_picktime
                    d.attrs["site_class"] = waveform.site_class
                    d.attrs["epicentral_distance"] = waveform.epicentral_distance
                    d.attrs["pga"] = waveform.pga
                    d.attrs["pgv"] = waveform.pgv
                    d.attrs["pgd"] = waveform.pgd
                    d.attrs["sampling_rate"] = waveform.sampling_rate
                    d.attrs["component_order"] = waveform.component_order
                    d.attrs["p_arrival_sample"] = waveform.p_arrival_sample
                    d.attrs["s_arrival_sample"] = waveform.s_arrival_sample
                    d.attrs["stream_starttime"] = str(waveform.stream_starttime)
                    d.attrs["channel_code"] = waveform.channel_code
                    d.attrs["network_code"] = waveform.network_code                    

                except:
                    continue            

    def add_events(self, event):
        self.events.append(event)

    def load_metadata(self, metadata_file):
        df = pd.read_csv(metadata_file)
        #df = df[(df.trace_category == 'earthquake_local') & (df.source_distance_km <= 20) & (df.source_magnitude > 3)]


### Class for event
class Event:
    def __init__(self, event_id, magnitude):
        self.event_id = event_id
        self.magnitude = magnitude
        self.waveforms = []

    def add_waveform (self, waveform):
        self.waveforms.append(waveform)

## Waveform classes
class Waveform:
    def __init__(self, event_id, station_id, channel_code, df):
        self.event_id = event_id
        self.station_id = station_id
        self.channel_code = channel_code
        self.wave_id = event_id + station_id
        self.df = df
        self.p_wave_picktime = df["p_wave_picktime"].values[0]
        self.s_wave_picktime = df["s_wave_picktime"].values[0]
        self.site_class = df["SiteClass"].values[0]
        self.epicentral_distance = df["epicentral_distance"].values[0]
        self.pga = df["PGA_new"].values[0]
        self.pgv = df["PGV_new"].values[0]
        self.pgd = df["PGD_new"].values[0]
        self.component_order = "ZNE"
        self.data = {}
        self.s_arrival_sample = None
        self.s_arrival_sample = None
        self.wave_starttime = None
        self.network_code = "NZ" # Hardcoded to NZ 

    def load_data(self, dataZ, dataN, dataE):
        dz = self.stream_to_numpy_flat(dataZ)
        dn = self.stream_to_numpy_flat(dataN)
        de = self.stream_to_numpy_flat(dataE)
        min_length = min(len(dz), len(dn), len(de))
        self.data = [dz[:min_length],dn[:min_length],de[:min_length]]
        self.sampling_rate = dataZ[0].stats.sampling_rate
        self.stream_starttime = dataZ[0].stats.starttime
        self.p_arrival_sample = self.get_wave_pick("p")
        self.s_arrival_sample = self.get_wave_pick("s")

    # Implement direct plotting here 
    def get_wave_pick(self, wavetype):
        if (wavetype == "p"):
            p_wave_arrival_time = UTCDateTime(self.p_wave_picktime)
            sample_offset = int((p_wave_arrival_time - self.stream_starttime) * self.sampling_rate)
            return sample_offset
        else:
            s_wave_arrival_time = UTCDateTime(self.s_wave_picktime)
            sample_offset = int((s_wave_arrival_time - self.stream_starttime) * self.sampling_rate)
            return sample_offset
        

    def stream_to_numpy_structured(self, stream):
        n_traces = len(stream)
        dtype = [('channel', 'S4'), ('data', float, (stream[0].data.shape[0],))]

        # Handle potential mismatched data lengths
        data_lengths = [trace.data.shape[0] for trace in stream]
        max_length = max(data_lengths)
        for i in range(n_traces):
            if stream[i].data.shape[0] < max_length:
                stream[i].data = np.pad(stream[i].data, (0, max_length - stream[i].data.shape[0]), mode='constant')

        data = np.empty(n_traces, dtype=dtype)
        for i, trace in enumerate(stream):
            data[i]['channel'] = trace.id
            data[i]['data'] = trace.data

        return data

    def stream_to_numpy_flat(self, stream):
        data = np.concatenate([trace.data for trace in stream])
        return data
