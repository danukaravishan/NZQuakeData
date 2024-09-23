import csv
import pandas as pd
import sys
import h5py
import os
import numpy as np
import obspy
from obspy import Trace

def create_local_eq_dict(eqfile):
    earthquake_map = {}
    with open(eqfile, 'r') as file:
        reader = csv.reader(file)
        first_row = True
        for row in reader:
            if first_row:
                first_row = False; 
                pass
            else:
                key = row[0]+row[1] # Set the key as <earthquakeID>+<stationName>
                earthquake_map[key] = row
    
    return earthquake_map

def hdf_to_csv(hdf_path, metadata_path, csv_path):


    df = pd.read_csv(metadata_path)

    ev_list = df['Earthquake Key'].to_list()
    dtfl = h5py.File("data\waveforms.hdf5", 'r')

    f = open(csv_path, 'ab')

    for c, evi in enumerate(ev_list):
        dataset = dtfl.get(evi) 
        if dataset == None :
            continue

        data = np.array(dataset)
        np.savetxt(f, data, delimiter = ",")


def main():
    base_path = os.getcwd()
    database_dir = base_path + "\data"
    metadata_path = database_dir + "\metadata.csv"
    waveforms_path = database_dir + "\waveforms.hdf5"

    fpath = "C:\\Users\\DANUKA\\Desktop\\OneDrive - Massey University\\Projects\\seismic_dataset\\data\\waveforms.hdf5"
    csv_file = "C:\\Users\\DANUKA\\Desktop\\OneDrive - Massey University\\Projects\\seismic_dataset\\data\\waveforms.csv"
    hdf_to_csv(metadata_path,metadata_path, csv_file)



# Takes dataset object as the input. dataset object has the wave attributes.
