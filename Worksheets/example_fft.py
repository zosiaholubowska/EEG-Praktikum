import numpy
import mne
from pathlib import Path
from matplotlib import pyplot as plt

def fourier_transform(data, samplerate, show=True, xlim=None, axis=None, return_fourier=False):
    nyquist = samplerate / 2
    n_samples = len(data)
    time = numpy.arange(0, n_samples) / n_samples
    fourier = numpy.zeros(n_samples, dtype=complex)
    frequencies = numpy.linspace(0, nyquist, int(n_samples / 2) + 1)
    for frequency in range(n_samples):
        sine_wave = numpy.exp(-1j * (2 * numpy.pi * frequency * time))
        fourier[frequency] = numpy.sum(sine_wave * data)
    fourier = fourier / n_samples
    spectrum = numpy.abs(fourier)[:int(n_samples / 2) + 1] ** 2
    if show:
        if not axis:
            fig, axis = plt.subplots(1, 1)
            axis.plot(frequencies, spectrum)
            axis.set_ylabel('Power (dB)')
            axis.set_xlabel('Frequency (Hz)')
        if xlim:
            axis.set_xlim(xlim[0], xlim[1])
    if return_fourier: return fourier, axis
    else: return axis


# --- Exercise 1: Making waves --- #

samplerate = 500  # what is a samplerate?

# duration of the signal (in seconds)
duration = ... # todo
signal_length = duration * samplerate

# create a time axis (array of time points)
time = numpy.linspace(start=0, stop=duration, num=signal_length)  # start, stop, number of steps

# --- make a sine wave:

# parameters of the sine wave:
amplitude = ...  # todo
frequency = ...  # todo
phi = numpy.sin(...)  # phase angle (0°-360°)  # todo
wave = amplitude * numpy.sin(2 * numpy.pi * frequency * time + phi)

# plot:
# - the sine wave
plt.figure()
plt.plot(time, wave)
plt.xlabel('Time (s)')
# - the spectrum of the sine wave
fourier_transform(data=wave, samplerate=500, show=True)


# --- add some sine waves together
frequencies = [...]  # list of different frequencies # todo
sine_waves = []
for freq in frequencies:
    x = amplitude * numpy.sin(2 * numpy.pi * freq * time + phi)
    sine_waves.append(x)
resulting_wave = numpy.sum(sine_waves, axis=0)

# plot
# - the resulting wave
plt.figure()
plt.plot(time, resulting_wave)
plt.xlabel('Time (s)')
# - its spectrum
fourier_transform(data=resulting_wave, samplerate=500, xlim=(0,10))


# --- generate a noisy signal (array of random values)
noise = numpy.random.uniform(-.5, .5, [signal_length])

# add our noise to the wave:
noisy_wave = resulting_wave + noise
# plot
plt.figure()
plt.plot(time, noisy_wave)
plt.xlabel('Time (s)')
fourier_transform(data=noisy_wave, samplerate=500, show=True, xlim=(0,100))




# --- Exercise 2: Filter your data --- #

# load some data
header_file = Path.cwd() / 'resources' / 'EEG_data' / 'P1_Ears Free_0.vhdr'
raw = mne.io.read_raw_brainvision(header_file, preload=True)

data = raw.pick_channels(['9'])._data[0][50000:51000]   # single channel eeg data
n_samples = len(data)  # length of the data (time-sequence)
time = numpy.arange(0, n_samples) / n_samples  # time points in the data

# take a look at the EEG (time series) data:
fig, ax = plt.subplots(1, 1)
ax.plot(time, data)
ax.set_ylabel('Amplitude (mV)')
ax.set_xlabel('Time (s)')
ax.set_title('Raw signal')


# ---- Step I: Fourier transformation

samplerate = 500        # sampling rate in Hz
nyquist = samplerate / 2    # Nyquist frequency -- the highest frequency you can measure in the data
# initialize Fourier output array
fourier = numpy.zeros(n_samples, dtype=complex)
# These are the actual frequencies in Hz that will be returned by the
# Fourier transform. The number of unique frequencies we can measure is
# exactly 1/2 of the number of data points in the time series (plus DC).
frequencies = numpy.linspace(0, nyquist, int(n_samples/2)+1)
# Fourier transform is dot-product between sine wave and data at each frequency
for frequency in range(n_samples):
    sine_wave = numpy.exp(-1j * (2 * numpy.pi * frequency * time))  # complex sine wave
    fourier[frequency] = numpy.sum(sine_wave * data)  # dot product
fourier = fourier / n_samples  # rescale by signal length

# to obtain the spectrum, disregard the complex part and convert to log power:
# (we keep the fourier transform ('fourier'-variable) to reconstruct the time series data after filtering)
spectrum = numpy.abs(fourier)[:int(n_samples / 2) + 1] ** 2

#  plot the spectrum
fig, ax = plt.subplots(1, 1)
ax.plot(frequencies, spectrum)
ax.set_ylabel('Power (dB)')
ax.set_xlabel('Frequency (Hz)')

# extra: plot a complex sine wave
# frequency = 3  # frequency of the sine wave in Hz
# fig = plt.figure()
# ax = plt.axes(projection='3d')
# sine_wave = numpy.exp(-1j * (2 * numpy.pi * frequency * time))  # complex sine wave
# ax.plot(time, sine_wave.real, sine_wave.imag)
# ax.set_title('%i Hz sine wave' % frequency)


# ---- Step II Construct a band pass filter

# get variables (these are the same variables as above)
nyquist = samplerate / 2  # Nyquist frequency -- the highest frequency you can measure in the data
frequencies = numpy.linspace(0, nyquist, int(n_samples / 2) + 1)

# create an array of zeros with the same length as the frequency array
# filter = numpy.zeros(len(frequencies))  # side note: this filter would just zero out all frequency components!
filter = numpy.zeros(n_samples)  # side note: this filter would just zero out all frequency components!

# select frequencies in the pass-band (the frequency components we want to keep)
low_frequency = 1
high_frequency = 40
passband_indices = numpy.where(numpy.logical_and(frequencies > low_frequency, frequencies < high_frequency))

# Create the filter kernel in the frequency domain: set value at the frequencies that we want to keep to 1, all others remain zero
filter[passband_indices] = 1
# plot the resulting filter
fig, ax = plt.subplots(1, 1)
ax.plot(frequencies, filter[:int(n_samples / 2) + 1])
ax.set_ylabel('Power (dB)')
ax.set_xlabel('Frequency (Hz)')

# Apply the filter to the spectrum (simply multiply the filter with the spectrum) and plot the resulting spectrum
filtered_fourier = fourier * filter

# to obtain the filtered version of the spectrum, disregard the complex part and convert to log power:
filtered_spectrum = numpy.abs(filtered_fourier)[:int(n_samples / 2) + 1] ** 2
fig, ax = plt.subplots(1, 1)
ax.plot(frequencies, filtered_spectrum)
ax.set_ylabel('Power (dB)')
ax.set_xlabel('Frequency (Hz)')
# compare the filtered spectrum to the original spectrum from above


# ---- Step III: Inverse Fourier transformation

# after we applied the filter to the spectrum of the signal
# we compute the inverse fourier transformation to recover the time series data
reconstructed_data = numpy.zeros(len(data))
for frequency in range(n_samples):
    #  scale sine waves by fourier coefficients
    sine_wave = filtered_fourier[frequency] * numpy.exp(1j * 2 * numpy.pi * (frequency) * time)
    # sine_wave = numpy.exp(-1j * (2 * numpy.pi * frequency * time))  # complex sine wave
    # sum sine waves together (take only real part)
    reconstructed_data = reconstructed_data + numpy.real(sine_wave)

# plot filtered time series
fig, ax = plt.subplots(1, 1)
ax.plot(time, reconstructed_data)
ax.set_ylabel('Amplitude (mV)')
ax.set_xlabel('Time (s)')
ax.set_title('Filtered signal')