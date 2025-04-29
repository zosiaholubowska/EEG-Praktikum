import mne
import json
import os

DIR = os.getcwd()
header_file_path = f"{DIR}/Data/EEG_data/blinks.vhdr"
raw = mne.io.read_raw_brainvision(header_file_path, preload=True)

# If you have multiple EEG recordings (blocks) of the same experiment,
# you can concatenate the raw files using mne.concatenate_raws()
# eeg_data_folder = f'{DIR}/Data/EEG_data'
# header_files = [file for file in os.listdir(eeg_data_folder) if ".vhdr" in file]
# raw = mne.concatenate_raws(
#     [mne.io.read_raw_brainvision(header_folder / header_file, preload=True) for header_file in header_files])

# Load channel mapping data
with open(f"{DIR}/Data/settings/mapping.json") as file:
    mapping = json.load(file)

raw.rename_channels(mapping)

# Load the montage of the cap
montage = mne.channels.make_standard_montage('brainproducts-RNP-BA-128')

raw.set_montage(montage)

# Plot the sensors of the raw object
# What do you notice?
raw.plot_sensors(show_names=True)

# Add reference channel that is named "FCz"
raw.add_reference_channels('...') # todo
raw.set_montage(montage)

# Plot the sensors of the raw object again
raw.plot_sensors(show_names=True)

# Now plot them in 3D
raw.plot_sensors(show_names=True, kind="...") # todo

# Make a copy of your raw data and filter it
raw_filtered = raw.copy().filter(...) # todo

# Create a copy of your raw data and mark the bad channels in it
raw_bads = raw_filtered.copy()
raw_bads.plot()

# Use the copy to repair the bad channels by interpolating (search the MNE documentation for the right function)
raw_interpolated = ... # todo
print(raw_interpolated.info["bads"])

raw_interpolated.plot()

# Extra: choose one of the channels that you marked "bad". Using the electrode map, pick the electrodes that are
# the "bad" channel's neighbours. Create a new channel (array) with the average of these electrodes
# What's the difference between this average and the interpolated version above?

# Rerefence for
# - Global average
# - Mastoids
# - Frontal electrodes
# - Single channel on top of the scalp

raw_ref_avg = raw_interpolated.copy().set_eeg_reference(ref_channels="...")
raw_ref_mastoids = ...
raw_ref_frontal = ...
raw_ref_FCz = ...

# Plot your raw signal after rereferencing for these different configurations
# What are the differences that you can see?

# Plot the power spectral density (PSD) and select the frequencies in the alpha range (8-12Hz)
# At which electrodes do you pick up most of the alpha activity?

# Save your final version of the raw data, so that you don't have to repeat these steps again
raw_ref_avg.save(...)

# Search for a python package that has an automated approach to bad channel detection and interpolation
# Try to use it!
