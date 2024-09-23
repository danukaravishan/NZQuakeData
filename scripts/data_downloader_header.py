import seisbench
import obspy
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNException
import matplotlib.pyplot as plt


def get_event_params(event):
    origin = event.preferred_origin()
    mag = event.preferred_magnitude()

    source_id = str(event.resource_id)

    event_params = {
        "source_id": source_id,
        "source_origin_time": str(origin.time),
        "source_origin_uncertainty_sec": origin.time_errors["uncertainty"],
        "source_latitude_deg": origin.latitude,
        "source_latitude_uncertainty_km": origin.latitude_errors["uncertainty"],
        "source_longitude_deg": origin.longitude,
        "source_longitude_uncertainty_km": origin.longitude_errors["uncertainty"],
        "source_depth_km": origin.depth / 1e3,
        "source_depth_uncertainty_km": origin.depth_errors["uncertainty"] / 1e3,
    }

    if mag is not None:
        event_params["source_magnitude"] = mag.mag
        event_params["source_magnitude_uncertainty"] = mag.mag_errors["uncertainty"]
        event_params["source_magnitude_type"] = mag.magnitude_type
        event_params["source_magnitude_author"] = mag.creation_info.agency_id
    
    return event_params


def get_trace_params(pick):
    net = pick.waveform_id.network_code
    sta = pick.waveform_id.station_code

    trace_params = {
        "station_network_code": net,
        "station_code": sta,
        "trace_channel": pick.waveform_id.channel_code[:2],
        "station_location_code": pick.waveform_id.location_code,
    }

    return trace_params

def get_waveforms(client, pick, trace_params, time_before=60, time_after=60):
    t_start = pick.time - time_before
    t_end = pick.time + time_after
    
    try:
        waveforms = client.get_waveforms(
            network=trace_params["station_network_code"],
            station=trace_params["station_code"],
            location="*",
            channel=f"{trace_params['trace_channel']}*",
            starttime=t_start,
            endtime=t_end,
        )
    except FDSNException:
        # Return empty stream
        waveforms = obspy.Stream()
    
    return waveforms