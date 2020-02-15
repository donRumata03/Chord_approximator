import os

from Peack_detector import *
import numpy as np
from scipy.io import wavfile


def normalize_harmonics(harm):
    res = harm[:]
    for i in range(len(harm)):
        res[i] = (res[i][0], harm[i][1].real)
    base_freq = res[0][0]
    mid_amp = sum(np.array(res).T[1]) / len(res)
    for index, val in enumerate(res):
        res[index] = (val[0] / base_freq, val[1] / mid_amp)

    return res


class Instrument:
    harmonics = []

    def __init__(self, instrument_file = None, music_file : str = None, _harmonics : list = None, raw_spectrum : list = None,
                 start_sample = 0, sample_width = None, noise_edge = None, sigma = None, peek_edge = None):

        if instrument_file is None and _harmonics is None and raw_spectrum is None and music_file is None:
            raise ValueError("Specify data for loading!")

        if music_file is not None:
            params = peek_detect_params(noise_edge=0.001 if noise_edge is None else noise_edge, sigma=0.3 if sigma is None else sigma)
            self.harmonics = normalize_harmonics(detect_file_peaks(
                music_file, sample_size=sample_width, sample_start=start_sample, params=params, debug=True))

        elif _harmonics is not None:
            self.harmonics = normalize_harmonics(_harmonics)

        elif raw_spectrum is not None:
            # TODO: ...
            pass

        elif instrument_file is not None:
            lines = open(instrument_file, "r").read().strip().splitlines()
            for l in lines:
                s = l.split(" : ")
                self.harmonics.append((float(s[0]), float(s[1])))


    def play_to_file(self, filename, base_freq = 440, duration = 2.0, fs = 48000): # duration : in seconds
        samples = np.arange(duration * fs) / fs

        # signal = np.sin(2 * np.pi * duration * samples)

        signal = np.array([0. for _ in range(len(samples))])


        for f, amp in self.harmonics:
            signal += amp * np.sin(2 * np.pi * f * base_freq * samples)

        signal /= max(signal)
        signal *= (2 ** 31 - 1)
        signal = np.int32(signal)
        print("Playing to:", filename)
        wavfile.write(filename, fs, signal)

    def to_file(self, filename):
        file_ending = ".instrument"
        if filename[-len(file_ending):] != file_ending:
            filename = filename + file_ending

        print("Saving to:", filename)

        file = open(filename, "w")

        for_file = []

        for val in self.harmonics:
            for_file.append(str(val[0]) + " : " + str(val[1]) + "\n")

        file.write("".join(for_file))


def parse_folder(folder : str, destination : str, play_folder : str = None):
    music_format = ".wav"
    l = os.listdir(folder)
    wavs = []
    for p in l:
        if p[-len(music_format):] == music_format:
            wavs.append(p)
    print(f"Generating instrument for these {music_format} files:", wavs)

    for note_file in wavs:
        this_instr = Instrument(music_file=folder + "/" + note_file)
        this_res_path = destination + note_file[:-len(music_format)] + ".instrument"
        this_instr.to_file(this_res_path)
        if play_folder is not None:
            this_instr.play_to_file(play_folder + note_file[:-len(music_format)] + music_format)


def make_guitar():
    g = Instrument(music_file="music/guitar_test.wav", sample_width=2**13, start_sample=74000)
    g.to_file("test_guitar")
    g.play_to_file("guitar_play.wav")



if __name__ == '__main__':
    # parse_folder("Notes/Piano", "Instruments/Piano")
    make_guitar()