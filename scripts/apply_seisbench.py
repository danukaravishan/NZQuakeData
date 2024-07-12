import obspy
import seisbench
import seisbench.models as sbm
import torch
from obspy.clients.fdsn import Client
from obspy import UTCDateTime
import matplotlib.pyplot as plt


def data():
    #client = Client("GFZ")
    #t = UTCDateTime("2007/01/01 05:48:50")
    #stream = client.get_waveforms(network="CX", station="PB01", location="*", channel="HH?", starttime=t-100, endtime=t+100)

    #Not picking well with the GeoNet Data

    client = Client("GEONET")
    time = UTCDateTime("2024-04-06T23:37:00")
    stream = client.get_waveforms(network="NZ", station="WEL", location="*", channel="HH?", starttime=time-200, endtime=time+200)

    return stream


def main():
    fig = plt.figure(figsize=(15, 5))
    ax = fig.add_subplot(111)

    stream = data()

    for i in range(3):
        ax.plot(stream[i].times(), stream[i].data, label=stream[i].stats.channel)
    ax.legend()

    model = sbm.EQTransformer.from_pretrained("original")
    print(model.weights_docstring)
    annotations = model.annotate(stream)
    print(annotations)

    fig = plt.figure(figsize=(15, 10))
    axs = fig.subplots(2, 1, sharex=True, gridspec_kw={'hspace': 0})

    offset = annotations[0].stats.starttime - stream[0].stats.starttime
    for i in range(3):
        axs[0].plot(stream[i].times(), stream[i].data, label=stream[i].stats.channel)
        if annotations[i].stats.channel[-1] != "N":  # Do not plot noise curve
            axs[1].plot(annotations[i].times() + offset, annotations[i].data, label=annotations[i].stats.channel)

    axs[0].legend()
    axs[1].legend()
    plt.show()
    
    model.save("EQtranformer_original.tf")

if __name__ == "__main__":
    main()
