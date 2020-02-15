import numpy as np
from scipy.io import wavfile

fs = 44100

f = int(input("Enter fundamental frequency: "))
t = float(input("Enter duration of signal (in seconds): "))

samples = np.arange(t * fs) / fs

signal = np.sin(2 * np.pi * f * samples)

signal *= (2 ** 31  - 1)

signal = np.int32(signal)

wavfile.write(input("Name your audio: "), fs, signal)