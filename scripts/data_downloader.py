### Author : Danuka Ravishan 
### Usage : Use the working directory as base, not the directory of script

import seisbench
import obspy
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNException
import matplotlib.pyplot as plt
from scripts.data_downloader_header import  get_event_params
from scripts.data_downloader_header import  get_trace_params
from scripts.data_downloader_header import  get_waveforms
import os
import pandas as pd
import seisbench.data as sbd
import seisbench.util as sbu
import h5py

client = Client("GEONET", timeout=10)

t0 = UTCDateTime(2020, 1, 1)
#t1 = UTCDateTime(2020, 3, 1)
t1 = t0 + 24 * 60  * 3 # 

base_path = os.getcwd() 
database_dir = base_path + "\data"
metadata_path = database_dir + "\metadata.csv"
waveforms_path = database_dir + "\waveforms.hdf5"

if not os.path.exists(database_dir):
    os.makedirs(database_dir)

catalog = client.get_events(t0, t1)

#start_time = UTCDateTime(2013, 1, 1, 0, 0, 0)
#end_time = UTCDateTime(2024, 6, 10, 23, 59, 59)

min_magnitude = 3.0
max_magnitude = 3.1
min_lat = -47.5617
max_lat = -34.2192
min_lon = 165.8271
max_lon = 179.6050

# catalog = client.get_events(starttime=t0, endtime=t1, minmagnitude=min_magnitude, maxmagnitude=max_magnitude, minlatitude=min_lat, maxlatitude=max_lat, minlongitude=min_lon, maxlongitude=max_lon)

# if os.path.exists(metadata_path) and os.path.exists(waveforms_path):
#     df = pd.read_csv(metadata_path)
#     database_exist_flag =  True
#     ev_list_raw = df['trace_name_original'].to_list()
#     ev_list = {}
#     for ev in ev_list_raw:
#         ev_list[ev] = 1
#     dtfl = h5py.File(waveforms_path, 'r')


with sbd.WaveformDataWriter (metadata_path, waveforms_path) as writer:
    # Define the data format
    writer.data_format = {
        "dimension_order": "CW",
        "component_order": "ZNE",
        "measurement": "velocity",
        "unit": "counts",
        "instrument_response": "not restituted",
    }

    # Iterate over the events and picks

    for event in catalog:
        event_params = get_event_params(event)
        for pick in event.picks:
            trace_params = get_trace_params(pick)
            waveforms = get_waveforms(client, pick, trace_params)

            
            # Skip processing existing events in the database
            # if (database_exist_flag and ev_list[trace_params["trace_name_original"]] == 1):
            #     continue;

            if len(waveforms) == 0:
                # No waveform data available
                continue
            
            sampling_rate = waveforms[0].stats.sampling_rate
            # Check that the traces have the same sampling rate
            assert all(trace.stats.sampling_rate == sampling_rate for trace in waveforms)

            actual_t_start, data, _ = sbu.stream_to_array(
                waveforms,
                component_order=writer.data_format["component_order"],
            )

            trace_params["trace_sampling_rate_hz"] = sampling_rate
            trace_params["trace_start_time"] = str(actual_t_start)

            sample = (pick.time - actual_t_start) * sampling_rate
            if (pick.phase_hint):
                trace_params[f"trace_{pick.phase_hint}_arrival_sample"] = int(sample)
                trace_params[f"trace_{pick.phase_hint}_status"] = pick.evaluation_mode

            trace_params["trace_name"] = event.resource_id.id.replace("smi:nz.org.geonet/","") + "-" + pick.waveform_id.station_code
            writer.add_trace({**event_params, **trace_params}, data)

