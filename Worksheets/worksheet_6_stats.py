from mne.channels import find_ch_adjacency, make_1020_channel_selections
import mne
from matplotlib import pyplot as plt
import os
import numpy

# Load epochs from the previously saved file
DIR = os.getcwd()
epochs = mne.read_epochs(f"{DIR}/Data/EEG_data/MMN_1-epo.fif")

# Let's repeat creating the evokeds from the epochs (Worksheet 5)

event_dict = {
    "standard": 1,
    "dev_freq": 2,
    "dev_loud": 3,
    "dev_dur": 4,
    "dev_loc": 5
}

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

# Select two conditions that you want to compare in your statistical test

# First, we calculate and plot the difference between the two conditions - as a results we will find, where our MMN was significant.
mmn_freq = mne.combine_evoked([evokeds['std_dev_freq'], evokeds['dev_freq']], weights=[-1, 1])
mmn_freq.plot_joint()

# Now we will perform a permutation cluster test on the data. If you want to understand the procedure in detail, you
# can read the paper "Nonparametric statistical testing of EEG- and MEG-data", but in short the approach is:
# 1. compute the difference between the conditions
# 2. assume the null hypothesis that the conditions are the same, meaning that the difference we are observing
# is purely by chance
# 3. randomly assign epochs to one condition (if they really were the same this should not matter)
# 4. compute the difference between the randomly assigned conditions
# --> repeat steps 3 & 4 again and again (like 1000 times or so)
# If the difference in our conditions was not merely a product of chance then the differences we observe in the
# randomly assigned conditions should rarely be as large as the original one.

# we will run the analysis across all channels so we need the adjacency matrix
adjacency, _ = mne.channels.find_ch_adjacency(epochs.info, "eeg")
plt.matshow(adjacency.toarray())  # take a look at the matrix

# the permutation test expects the data to be in the shape: observations × time × space.
# in our case, the observations are single epochs. You could also test across multiple subjects. In this case,
# one observation would be the evoked response of one subject.

# Standard pool for dev_freq = all but dev_freq
std_dev_freq_epochs = mne.concatenate_epochs([
    epochs["standard"],
    epochs["dev_loud"],
    epochs["dev_dur"],
    epochs["dev_loc"]
])

# Deviant condition
dev_freq_epochs = epochs["dev_freq"]

X = [std_dev_freq_epochs.get_data().transpose(0, 2, 1),
     dev_freq_epochs.get_data().transpose(0, 2, 1)]

# Calculate statistical thresholds. For times sake we are only doing 100 permutations but in a "real" analysis
# you would at least do 1000.
t_obs, clusters, cluster_pv, h0 = mne.stats.spatio_temporal_cluster_test(
    X, threshold=dict(start=.2, step=.2), adjacency=adjacency, n_permutations=100)

# We can see the number of significant points in the data by summing all the values in the test statistic which
# have a value smaller .05
significant_points = cluster_pv.reshape(t_obs.shape).T < .05
print(str(significant_points.sum()) + " points selected by TFCE ...")

# Visualize them in a plot (only significant points are shown in color):
mmn_freq.plot_image(mask=significant_points, show_names="all")

# You can also visualise your data, dividing into center, right, and left channels
selections = make_1020_channel_selections(mmn_freq.info, midline="12z")
fig, axes = plt.subplots(nrows=3, figsize=(8, 8))
axes = {sel: ax for sel, ax in zip(selections, axes.ravel())}
mmn_freq.plot_image(
    axes=axes,
    group_by=selections,
    colorbar=False,
    show=False,
    mask=significant_points,
    show_names="all",
    titles=None,
)
plt.colorbar(axes["Left"].images[-1], ax=list(axes.values()), shrink=0.3, label="µV")

plt.show()

# Try the entire process with different conditions!
# How would you check for statistical significance for more than one condition?
# How would you check for a linear trend in your data?

# How to extract the MMN amplitude?

# 1. Pick the channel
evoked_Fz = mmn_freq.copy().pick_channels(['Fz'])

# 2. Crop to 100–250 ms
evoked_Fz.crop(tmin=0.100, tmax=0.250)

# 3. Get the data and times
data = evoked_Fz.data[0]  # shape: (n_times,)
times = evoked_Fz.times   # shape: (n_times,)

# 4. Find time of the minimum value (MMN peak)
min_idx = numpy.argmin(data)
min_time = times[min_idx]
min_val = data[min_idx]

print(f"MMN minimum value at Fz: {min_val/1e-6:.3f} µV at {min_time*1000:.1f} ms")

# 5. Define 40 ms window centered at MMN peak
window_half_width = 0.020  # 20 ms on each side = 40 ms total
window_start = min_time - window_half_width
window_end = min_time + window_half_width

window_start = max(window_start, times[0])
window_end = min(window_end, times[-1])

# 6. Get the mean amplitude
window_mask = (times >= window_start) & (times <= window_end)
window_mean = data[window_mask].mean()

print(f"Mean amplitude in 40 ms window around MMN peak: {window_mean/1e-6:.3f} µV at {min_time*1000:.1f} ms")
