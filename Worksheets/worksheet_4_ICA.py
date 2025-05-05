# ICA
import mne
import json
import os
import matplotlib.pyplot as plt

DIR = os.getcwd()

# Load your most recently saved raw data
# Before we run the ICA, an important step is filtering the data to remove low-frequency drifts
# Make sure you filter your data or load the version that is already filtered

raw = ...

# Load channel mapping data if your previously saved data doesn't have it
with open(f'{DIR}/Data/settings/mapping.json') as file:
    mapping = json.load(file)
raw.rename_channels(mapping)
raw.add_reference_channels('FCz')
montage = mne.channels.make_standard_montage('brainproducts-RNP-BA-128')
raw.set_montage(montage)

# Set up the ICA function with default values
n_components = 15
ica_method = "fastica"
ica = mne.preprocessing.ICA(n_components=n_components, method=ica_method, random_state=97)
# What does the random_state mean? Why is it useful to define it?

# Fit the ICA function to your previously loaded data
ica.fit(raw)

# Plot the sources of the ICA results
ica.plot_sources(raw)
# Right-click on the name of the component to see its properties

# Plot the topomaps of the components of the ICA results
# By clicking on the unwanted component, you can select it to be excluded when applying the ICA to the data,
# similar to how you marked "bad" channels on your raw object
ica.plot_components()
plt.savefig("ICA_components.png", dpi=800)

# You can also select the unwanted ICA components manually by giving the component ID to the "exclude" list
ica.exclude = [...]

# Plot the raw data in overlay mode to highlight the differences between before and after ICA component removal
ica.plot_overlay(raw, exclude=ica.exclude, picks="eeg")

# Plot the properties of the component(s) that correspond to blinks. Repeat for eye movements!
ica.plot_properties(raw, picks=..., show=True) #todo

# Get the explained variance of each component. What does this mean?
explained_var_ratio = ica.get_explained_variance_ratio(raw)

# Reconstruct the raw signal without the excluded components using the apply function
raw_clean = ica.apply(raw.copy())

# Try rerunning the ICA process for data that is referenced at different electrodes
# What differences can you see in the components? And in the sources?

# Save your updated raw file after you are done with the ICA preprocessing
raw_clean.save(f'{DIR}/Data/EEG_data/MMN_1_ica-raw.fif')
# Extra: try to use the mne-icalabel package (https://mne.tools/mne-icalabel/dev/index.html)
# to automatically label the different components you have identified

