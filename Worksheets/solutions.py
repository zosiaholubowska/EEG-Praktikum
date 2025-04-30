import mne
import os
DIR = os.getcwd()

header_file_path = f"{DIR}/Data/EEG_data/MMN_1.vhdr"

raw = mne.io.read_raw_brainvision(header_file_path, preload=True)

raw.get_data().shape

raw.info

raw.ch_names

raw_copy = raw.copy()

import json
with open(f"{DIR}/Data/settings/mapping.json") as file:
    mapping = json.load(file)

raw_copy.rename_channels(mapping)

raw_copy.plot(block=True) #  pip install mne-qt-browser

picks = mne.pick_channels_regexp(raw_copy.ch_names, regexp="Fp")

raw_cut = raw_copy.get_data(picks=picks, start=0, stop=5000)

montage = mne.channels.make_standard_montage('brainproducts-RNP-BA-128')

raw_copy.set_montage(montage)

montage.plot()

raw_copy.save(f'{DIR}/Data/EEG_data/raw.fif', overwrite=True)