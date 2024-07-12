# Use the local database path create hdf5 file

import os
from obspy.core import read
from db_classes import *
from utills import *


## Below settings are for  building original database
# year = "2022"
# local_db_dir = "E:\\ADRIAN\\"+year+"\\"
# base_path = os.getcwd() 
# database_dir = "C:\\Users\\22008603\\Desktop\\eqdata"
# metadata_path = database_dir + "\metadata.csv"
# waveforms_path = database_dir + "\waveforms_"+year+".hdf5"
# prev_metadata_path = database_dir + "\prev_data.csv"
#####


local_db_dir = "D:\\WORK\\GeoNet Data\\eq_data\\"
database_dir = "C:\\Users\\DANUKA\\Desktop\\OneDrive - Massey University\\Projects\\seismic_dataset\\data\\"
metadata_path = database_dir + "\metadata.csv"
waveforms_path = database_dir + "\waveforms.hdf5"
prev_metadata_path = database_dir + "\prev_data.csv"


## Utills
if os.path.exists(waveforms_path):
    os.remove(waveforms_path)
#eq_metadata = create_local_eq_dict(prev_metadata_path)
df = pd.read_csv(prev_metadata_path)


### Read local Dir
db =  DatabaseWriter(waveforms_path)

for event in os.listdir(local_db_dir):

    # Get the magnitude
    a = df[df.EarthquakeID == event]["magnitude"]
    earthquake_magnitude = None
    if not a.empty:
        earthquake_magnitude = a.iloc[0]
    event_ob = Event(event, earthquake_magnitude)

    if not event.startswith('.'):
        directory_2 = local_db_dir + event + '/'
        for station in os.listdir(directory_2):
            if not station.startswith("TUWZ"):#to filter this station, lack of data
                if not station.startswith('.'):
                    dfwave = df[df.EventID == event+station]
                    if(dfwave.empty):
                        continue
                    if os.path.exists(directory_2 + station + '/' + "ACC" + "/" + 'HNZ-DATA.mseed'):
                        st_Z = read(directory_2 + station + '/' + "ACC" + "/" + 'HNZ-DATA.mseed') # Vertical
                        st_N = read(directory_2 + station + '/' + "ACC" + "/" + 'HNN-DATA.mseed') # North
                        st_E = read(directory_2 + station + '/' + "ACC" + "/" + 'HNE-DATA.mseed') # East
                        wave = Waveform (event, station, "HN", dfwave); wave.load_data(st_Z, st_N, st_E); event_ob.add_waveform(wave)
                    else:
                        st_Z = read(directory_2 + station + '/' + "ACC" + "/" + 'BNZ-DATA.mseed')
                        st_N = read(directory_2 + station + '/' + "ACC" + "/" + 'BNN-DATA.mseed')
                        st_E = read(directory_2 + station + '/' + "ACC" + "/" + 'BNE-DATA.mseed')                        
                        wave = Waveform (event, station, "BN", dfwave); wave.load_data(st_Z, st_N, st_E); event_ob.add_waveform(wave)

    print(event)
    db.add_events(event_ob)
    db.save_event_to_hdf(event_ob)

