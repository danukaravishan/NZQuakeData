from obspy import UTCDateTime
from obspy.clients.fdsn import Client
import obspy
import os

# Global Defs
c = Client("GEONET")
start_time = UTCDateTime(2013, 1, 1, 0, 0, 0)
end_time = UTCDateTime(2024, 3, 28, 23, 59, 59)
min_magnitude = 6.0
max_magnitude = 6.1
min_lat = -47.5617
max_lat = -34.2192
min_lon = 165.8271
max_lon = 179.6050

catalog = c.get_events(starttime=start_time, endtime=end_time, minmagnitude=min_magnitude, maxmagnitude=max_magnitude, minlatitude=min_lat, maxlatitude=max_lat, minlongitude=min_lon, maxlongitude=max_lon)

cur_dir = os.getcwd()
database_dir = cur_dir + "/data"
catalog_dir = database_dir + "/catalog/"


# while max_magnitude <= 6.8:
#     try:
#         catalog = c.get_events(starttime=start_time, endtime=end_time, minmagnitude=min_magnitude, maxmagnitude=max_magnitude, minlatitude=min_lat, maxlatitude=max_lat, minlongitude=min_lon, maxlongitude=max_lon)
#         ##write the catalog to a file called catalogue
#         catalog_fname = catalog_dir + "catalogue_between_"+str(min_magnitude)+"-"+str(max_magnitude)
#         if not (os.path.isfile(catalog_fname)):
#             catalog.write(catalog_fname, format="QUAKEML")
#             print(catalog)
#         min_magnitude = round((min_magnitude + 0.1),1)
#         max_magnitude = round((max_magnitude + 0.1),1)
#     except:
#         min_magnitude = round((min_magnitude + 0.1),1)
#         max_magnitude = round((max_magnitude + 0.1),1)

# Merge the catalog data

for filename in os.listdir(catalog_dir):
    print(filename)

    catalog = obspy.read_events(catalog_dir + "/" + filename, format="QUAKEML")
    print(catalog)
    print("\n\n\n ======= ")

    for event in catalog:
        print(event)