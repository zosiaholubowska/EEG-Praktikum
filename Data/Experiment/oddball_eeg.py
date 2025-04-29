import slab
import numpy
import random
import time
import freefield
from pathlib import Path
fs = 24414
slab.set_default_samplerate(fs)
data_dir = Path.cwd() / 'experiments'
rcx_file = 'play_buf.rcx'

# generate standard
f0 = 500
n_harmonics = 3
duration = 0.075
level = 80

# generate standard - EEG trigger code 1
standard = slab.Sound.tone(f0, duration, level=level)
standard += slab.Sound.tone(f0*2, duration, level=level-3)
standard += slab.Sound.tone(f0*3, duration, level=level-6)

# generate frequency deviant - EEG trigger code 2
dev_f0 = 550
deviant_1 = slab.Sound.tone(dev_f0, duration, level=level)
deviant_1 += slab.Sound.tone(dev_f0*2, duration, level=level-3)
deviant_1 += slab.Sound.tone(dev_f0*3, duration, level=level-6)

# generate loudness deviant - EEG trigger code 3
dev_level = level + 10
deviant_2 = slab.Sound.tone(f0, duration, level=dev_level)
deviant_2 += slab.Sound.tone(f0*2, duration, level=dev_level-3)
deviant_2 += slab.Sound.tone(f0*3, duration, level=dev_level-6)

# generate duration deviant - EEG trigger code 4
dev_duration = duration - 0.05
deviant_3 = slab.Sound.tone(f0, dev_duration, level=level)
deviant_3 += slab.Sound.tone(f0*2, dev_duration, level=level-3)
deviant_3 += slab.Sound.tone(f0*3, dev_duration, level=level-6)
silence = slab.Sound.silence(duration=.05)
deviant_3 = slab.Sound.sequence(deviant_3, silence)

# location deviant  - EEG trigger code 5
# handled in rcx

# (SOA) of 500 ms in three 5 min sequences
def run_experiment(n_trials=1845, soa = 0.5):
    # stimulus codes (0 - 4) appear in the trial sequence
    # eeg triggers: 1 - 5
    # 1: standard, 2 - 5: deviants
    # write stimulus data to buffers
    freefield.write('playbuflen', standard.n_samples, ['RX81', 'RX82'])
    freefield.write('std_data', standard.data, ['RX81', 'RX82'])
    freefield.write('dev_data_1', deviant_1.data, ['RX81'])
    freefield.write('dev_data_2', deviant_2.data, ['RX81'])
    freefield.write('dev_data_3', deviant_3.data, ['RX81'])

    freefield.write('dev_chan', 14, ['RX82'])

    # generate trial sequence
    sequence = generate_mmn_sequence(n_trials)
    trial_sequence = slab.Trialsequence(conditions=sequence)
    trial_sequence.trials = numpy.arange(n_trials).tolist()
    # trial_sequence.save_csv(save_csv_path)    # Save to CSV

    stim_codes = [0, 1, 2, 3]
    channels=['std_chan', 'dev_chan_1', 'dev_chan_2', 'dev_chan_3']

    # Run trials
    print("\nStarting MMN experiment...\n")

    for stim_code in (trial_sequence):
        freefield.write('trigcode', stim_code, ['RX81', 'RX82'])
        # halt every 615 stmiuli
        if stim_code == 4:  # play deviant location
            freefield.write('std_chan', 14, ['RX82'])
            for code in stim_codes:  # set all other channels to 25
                freefield.write(channels[code], 25, ['RX81'])
            freefield.play('zBusA')
            freefield.wait_to_finish_playing()
            freefield.write('std_chan', 25, ['RX82'])

        else:  # play standard location
            freefield.write(channels[stim_code], 1, ['RX81'])
            for code in list(filter(lambda x: x != stim_code, stim_codes)):  # set all other channels to 25
                freefield.write(channels[code], 25, ['RX81'])
            freefield.play('zBusA')
            freefield.wait_to_finish_playing()

        time.sleep(soa-standard.duration)
        if trial_sequence.this_n == 615 or trial_sequence.this_n == 1230:
            input('Press enter to continue...')

    print("\nExperiment complete.")

def init_dsp(rcx_file):
    proc_list = [['RX81', 'RX8', data_dir / rcx_file],
                 ['RX82', 'RX8', data_dir / rcx_file]]
    freefield.initialize('dome', device=proc_list, sensor_tracking=False)
    # freefield.load_equalization(data_dir / '')

def generate_deviant_groups(total_deviants, last_deviant=None):
    deviant_types = [1, 2, 3, 4]
    groups = []
    while len(groups) * 5 < total_deviants:
        group = deviant_types.copy()
        # Choose a 5th deviant that's not same as previous group's last deviant
        extra_choices = [d for d in deviant_types if d != last_deviant]
        group.append(random.choice(extra_choices))
        # Shuffle group until no adjacent duplicates with previous group's end
        for _ in range(1000):
            random.shuffle(group)
            if last_deviant is None or group[0] != last_deviant:
                if all(group[i] != group[i+1] for i in range(len(group)-1)):
                    break
        else:
            raise RuntimeError("Failed to build a valid deviant group.")
        groups.append(group)
        last_deviant = group[-1]
    # Flatten list of groups
    return [d for group in groups for d in group]

def generate_mmn_sequence(n_trials, leading_standards=15):
    if n_trials <= leading_standards or (n_trials - leading_standards) % 2 != 0:
        raise ValueError("Total length must allow alternation after leading standards.")
    sequence = [0] * leading_standards
    num_deviants = (n_trials - leading_standards) // 2
    deviant_list = generate_deviant_groups(num_deviants)
    # Interleave with standards
    for deviant in deviant_list:
        sequence.append(deviant)  # odd index
        sequence.append(0)        # even index
    return sequence[:n_trials]

if __name__ == "__main__":
    init_dsp(rcx_file)
    run_experiment()



# some ideas:
# timbre: create a sound that has the same f0 and amplitude/mean power across frequencies, but different:
# 1 Range between tonal and noiselike character
# 2 Spectral envelope
# 3 Time envelope in terms of rise, duration, and decay (ADSR, which stands for "attack, decay, sustain, release")
# 4 Changes both of spectral envelope (formant-glide) and fundamental frequency (micro-intonation)
# 5 Prefix, or onset of a sound, quite dissimilar to the ensuing lasting vibration

# location (shift itd and ild independently? - ask kirke)

# tradeoff between HRTF and Timbre:
# happens on the spectral envelope level: timbre -> ratio of power across harmonics, hrtf -> ratio of power across bands
# change timbre by playing through known and unknown HRTF?
# behavioral difference? behavioral ratings? unknown HRTF should differ (use jnd timbre differences)
# ask participants to localize first and then rate timbre or reverse or simultaneously
# test spatial instruments for timbre changes