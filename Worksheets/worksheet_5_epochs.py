# Epochs and Evokeds
import mne
import json
import os
import matplotlib.pyplot as plt

DIR = os.getcwd()
raw = ...

# Load events and the event_id dictionary with the unique event values
events, event_id = mne.events_from_annotations(raw)

# Visualise all events and their types
mne.viz.plot_events(events, sfreq=raw.info["sfreq"], first_samp=raw.first_samp, event_id=event_id)

# Create epochs based on the events list and define the time points of interest before and after the event
t_min = -0.1
t_max = 0.5
epochs = mne.Epochs(raw, events, tmin=t_min, tmax=t_max)

# Print the epochs object and notice the names of the event_ids
print(epochs)


# Redefine your event_id dictionary to name events for easier referencing later on
event_dict = {
    "standard": 1,
    "dev_freq": 2,
    "dev_loud": 3,
    "dev_dur": 4,
    "dev_loc": 5
}
epochs = mne.Epochs(raw, events, tmin=t_min, tmax=t_max, event_id=event_dict)
print(epochs.event_id)

# Now it's easy to subselect epochs using square brackets
print(epochs["standard"])
print(epochs[["dev_freq", "..."]])

# Create another epochs object but this time reject epochs based on peak-to-peak channel amplitude
reject_criteria = ...
flat_criteria = ...
epochs = mne.Epochs(raw, events, tmin=t_min, tmax=t_max, event_id=event_dict, reject=reject_criteria, flat_criteria=flat_criteria)
# Plot the estimation of how many epochs were rejected based on the parameters (search for "drop log")
epochs.plot...

# Plot the first 10 epochs with the notation
epochs.plot(n_epochs=..., events=True)

# Baseline correction: select the time points in which you want to correct for baseline
# and apply it to the epochs object
epochs.apply_....

# Save the epochs as a new file
# Epochs objects can be saved in the .fif format
# The MNE-Python naming convention for epochs files is that the file basename
# (the part before the .fif or .fif.gz extension) should end with -epo or _epo,
# and a warning will be issued if the filename you provide does not adhere to that convention.
epochs.save(f"{DIR}/Data/EEG_data/MMN_1-epo.fif", overwrite=True)

# Search for a python package that has an automated approach to bad channel detection and interpolation
# Try to use it!

# Evoked objects are the averages of all epochs relating to the same experimental condition (event_id)
conditions = list(event_dict.keys())
evokeds = [epochs[condition].average() for condition in conditions]

# Plot the evoked of each of the conditions
evokeds[0].plot()
evokeds[1].plot()
...

# Plot the evoked of each of the conditions with a topomap view of the most prominent peaks
# Explore other plotting options on the evoked data to see which ones represent your results the best
evokeds[0].plot_joint()
evokeds[1].plot_joint()
...

# Plot the evoked objects to be able to compare conditions
# Plot the global field power (GFP), as well as pick one channel for best representation of your experiment
# What's the difference between the plots?
mne.viz.plot_compare_evokeds(evokeds)

# Get peak amplitude and the time points of the peaks for each condition

# Save the evokeds object as a .fif file
mne.write_evokeds(f"{DIR}/Data/EEG_data/MMN_1-ave.fif", evokeds, overwrite=True)

# Now try to create the evokeds for our paradigm.
# Standard - all other conditions than deviant.

evokeds = {}
deviants = [cond for cond in event_dict if cond != "standard"]

for dev in deviants:
    print(f"Processing: {dev}")

    # Collect the joint standard: all except the current deviant
    joint_std_conds = ["standard"] + [d for d in deviants if d != dev]
    joint_std_epochs = mne.concatenate_epochs([epochs[c] for c in joint_std_conds])

    # Get the deviant epochs
    dev_epochs = epochs[dev]

    # Average and append
    evokeds[f'std_{dev}'] = joint_std_epochs.average()  # joint standard
    evokeds[dev] = dev_epochs.average()  # deviant

# This part of the code can change, depending on your research question.
# I will give you couple of exaples of what you can do with your data now to visualise MMN.

mmn_freq = mne.combine_evoked([evokeds['std_dev_freq'], evokeds['dev_freq']], weights=[-1, 1])

# Plot the difference waves on all electrodes

mne.viz.plot_compare_evokeds(
    {'Deviant':evokeds['dev_freq'], 'Standard': evokeds['std_dev_freq'], 'MMN': mmn_freq},
    picks="eeg",
    axes="topo",
)

# Plot the difference waves on selected region of interest

mne.viz.plot_compare_evokeds([evokeds['dev_freq'], evokeds['std_dev_freq'], mmn_freq],
                              combine='mean',
                              legend='lower right',
                              picks=['FCz', 'Fz', 'F1', 'F2'],
                              show_sensors='upper right',
                              )

# Plot the topography of the difference waves

fig = mmn_freq.plot_topomap(0.15, average=0.1)

# Try to extract the amplitude for the MMN (you can try single electrode or ROI)
# Try to extract the latency of the MMN

