import pandas as pd
import h5py
import numpy as np
import matplotlib.pyplot as plt

def iqr_outlier_removal(data):
  """
  This function removes outliers based on Interquartile Range (IQR).
  """
  q1 = np.percentile(data, 25)
  q3 = np.percentile(data, 75)
  iqr = q3 - q1
  lower_bound = q1 - (1.5 * iqr)
  upper_bound = 2.5
  return data[(data >= lower_bound) & (data <= upper_bound)]


def plot_time(filename):
    # Read the data from the file
    data = []
    with open(filename, 'r') as f:
        for line in f:
        # Convert string value to float
            data.append(float(line.strip()))

    # Convert data to a NumPy array for easier manipulation
    data_array = np.array(data)

    #Remove outliers
    data_array_without_outliers = iqr_outlier_removal(data_array.copy())

    # Apply moving average
    window_size = 1000
    smoothed_data = np.convolve(data_array_without_outliers, np.ones(window_size)/window_size, mode='valid')
    # Create the time axis (assuming data points are at regular intervals)
    time_axis = np.arange(len(smoothed_data))  # Creates an array from 0 to length-1

    # Customize the plot (optional)
    plt.figure(figsize=(10, 6))  # Set plot size
    plt.xlabel("Annotation index", fontsize=22, fontweight='bold')
    plt.ylabel("Inference Time (s)", fontsize=22, fontweight='bold')
    plt.title("Inference Time Variation", fontsize=30, fontweight='bold', pad=25)

    # Plot the data
    plt.plot(time_axis, smoothed_data)

    # Show the plot
    plt.grid(True)
    for spine in plt.gca().spines.values():
        spine.set_linewidth(2)  # Adjust the line width to make it bold

    plt.show()

# Open the HDF5 file
def plot_waveforms():
    waveform_file = 'D:\WORK\STEAD\chunk2.hdf5'
    metadata_file = 'D:\WORK\STEAD\chunk2.csv'

    df = pd.read_csv(metadata_file)
    df = df[(df.trace_category == 'earthquake_local') & (df.source_distance_km <= 20) & (df.source_magnitude > 3)]

    print(f'total events selected: {len(df)}')

    ev_list = df['trace_name'].to_list()
    dtfl = h5py.File(waveform_file, 'r')


    for c, evi in enumerate(ev_list):
        dataset = dtfl.get('data/'+str(evi)) 
        # waveforms, 3 channels: first row: E channel, second row: N channel, third row: Z channel 
        data = np.array(dataset)

        fig = plt.figure()
        ax = fig.add_subplot(311)         
        plt.plot(data[:,0], 'k')
        plt.rcParams["figure.figsize"] = (8, 5)
        legend_properties = {'weight':'bold'}    
        plt.tight_layout()
        ymin, ymax = ax.get_ylim()
        pl = plt.vlines(dataset.attrs['p_arrival_sample'], ymin, ymax, color='b', linewidth=2, label='P-arrival')
        sl = plt.vlines(dataset.attrs['s_arrival_sample'], ymin, ymax, color='r', linewidth=2, label='S-arrival')
        cl = plt.vlines(dataset.attrs['coda_end_sample'], ymin, ymax, color='aqua', linewidth=2, label='Coda End')
        plt.legend(handles=[pl, sl, cl], loc = 'upper right', borderaxespad=0., prop=legend_properties)        
        plt.ylabel('Amplitude counts', fontsize=12) 
        ax.set_xticklabels([])

        ax = fig.add_subplot(312)         
        plt.plot(data[:,1], 'k')
        plt.rcParams["figure.figsize"] = (8, 5)
        legend_properties = {'weight':'bold'}    
        plt.tight_layout()
        ymin, ymax = ax.get_ylim()
        pl = plt.vlines(dataset.attrs['p_arrival_sample'], ymin, ymax, color='b', linewidth=2, label='P-arrival')
        sl = plt.vlines(dataset.attrs['s_arrival_sample'], ymin, ymax, color='r', linewidth=2, label='S-arrival')
        cl = plt.vlines(dataset.attrs['coda_end_sample'], ymin, ymax, color='aqua', linewidth=2, label='Coda End')
        plt.legend(handles=[pl, sl, cl], loc = 'upper right', borderaxespad=0., prop=legend_properties)        
        plt.ylabel('Amplitude counts', fontsize=12) 
        ax.set_xticklabels([])

        ax = fig.add_subplot(313)         
        plt.plot(data[:,2], 'k')
        plt.rcParams["figure.figsize"] = (8,5)
        legend_properties = {'weight':'bold'}    
        plt.tight_layout()
        ymin, ymax = ax.get_ylim()
        pl = plt.vlines(dataset.attrs['p_arrival_sample'], ymin, ymax, color='b', linewidth=2, label='P-arrival')
        sl = plt.vlines(dataset.attrs['s_arrival_sample'], ymin, ymax, color='r', linewidth=2, label='S-arrival')
        cl = plt.vlines(dataset.attrs['coda_end_sample'], ymin, ymax, color='aqua', linewidth=2, label='Coda End')
        plt.legend(handles=[pl, sl, cl], loc = 'upper right', borderaxespad=0., prop=legend_properties)        
        plt.ylabel('Amplitude counts', fontsize=12) 
        ax.set_xticklabels([])
        plt.show() 
        inp = input("Press a key close!")
        if inp == "r":
            continue 

        for at in dataset.attrs:
            print(at, dataset.attrs[at])    

        inp = input("Press a key to plot the next waveform!")
        if inp == "r":
            continue 

def main():
    #plot_time("data/log/analysis/eqt/annotation.log")
    plot_time("data/log/analysis/eqt/annotation.log")


if __name__ == "__main__":
    main()
