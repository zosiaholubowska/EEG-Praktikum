# Import MNE python library
# link to the tutorials:
# https://mne.tools/stable/auto_tutorials/index.html
import mne

# Define paths
import os
DIR = os.getcwd()

# Define the file path of the header file
header_file_path = f"{DIR}/..."

# Read in the raw Brainvision file using the "io" class
raw = ...

# Print the raw object. How many channels are there? How many seconds is the recording?

# Print the list of all individual time points

# Print the "info" object of the raw variable. What is the sampling frequency?

# Print the list of all channel names

# Create a copy of the raw object and store it in a new variable

# Rename the channels on the copy of the raw object (use the electrode map image - mapping.json)

# Plot the raw file

# Select bad channels

# Print the names of the selected bad channels

# Pick all the channels that you would associate with blinking
# or pick all "frontal" channels using a regular expression (regexp)

# Create a new variable called raw_cut, in which you will store the first 10 s of the EEG recording

# Create montage, to define electrode positions
# We are using the BrainProducts system

# Plot montage

# Save the raw_copy variable as raw.fif in the EEG data folder




