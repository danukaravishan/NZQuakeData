from obspy.clients.fdsn import Client
from obspy import UTCDateTime
start_1 = "2024-05-01 00:00:00"
starttime = UTCDateTime(start_1)
endtime = starttime + 600       # 600 seconds
client = Client('https://data.raspberryshake.org') 
waveform = client.get_waveforms('AM', 'R13B6', '00', 'EHZ', starttime, endtime)
print(waveform)