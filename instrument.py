import os

from Peack_detector import *
import numpy as np
from scipy.io import wavfile


def normalize_harmonics(harm):
    res = harm[:]
    if not harm:
        return res
    for i in range(len(harm)):
        res[i] = (res[i][0], harm[i][1])

    base_freq = 0
    best_amp = -1
    for index, (freq, amp) in enumerate(res):
        if best_amp < amp:
            best_amp = amp
            base_freq = freq
    mid_amp = sum(np.array(res).T[1]) / len(res)
    for index, val in enumerate(res):
        res[index] = (val[0] / base_freq, val[1] / mid_amp)

    return res


class Instrument:
    harmonics = []

    def __init__(self, instrument_file = None, music_file : str = None, _harmonics : list = None, raw_spectrum : list = None,
                 start_sample = 0, sample_width = None, noise_edge = None, sigma = None, peek_edge = None):

        if instrument_file is None and _harmonics is None and raw_spectrum is None and music_file is None:
            pass
            # raise ValueError("Specify data for loading!")

        if music_file is not None:
            params = peek_detect_params(noise_edge=0.005 if noise_edge is None else noise_edge, sigma=0.3 if sigma is None else sigma)
            self.harmonics = normalize_harmonics(detect_file_peaks(
                music_file, sample_size=sample_width, sample_start=start_sample, params=params, debug=True))

        elif _harmonics is not None:
            self.harmonics = normalize_harmonics(_harmonics)

        elif raw_spectrum is not None:
            # TODO: ...
            pass

        elif instrument_file is not None:
            lines = open(instrument_file, "r").read().strip().splitlines()
            self.harmonics = []
            for l in lines:
                s = l.split(" : ")
                self.harmonics.append((float(s[0]), float(s[1])))


    def revise_harmonics(self):
        self.harmonics = normalize_harmonics(self.harmonics)

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
        this_instr = Instrument(music_file=folder + "/" + note_file, sample_width=2**14, start_sample=0)
        this_res_path = destination + note_file[:-len(music_format)] + ".instrument"
        this_instr.to_file(this_res_path)
        if play_folder is not None:
            this_instr.play_to_file(play_folder + note_file[:-len(music_format)] + music_format)


def make_guitar():
    g = Instrument(music_file="Notes/Piano/A.wav", sample_width=2**13, start_sample=0)
    g.to_file("test_guitar")
    g.play_to_file("guitar_play.wav")


def get_folder_instruments_names(folder_name : str) -> list:
    return [folder_name + "\\" + name for name in os.listdir(folder_name) if name[-len(".instrument"):] == ".instrument"]

def get_folder_instruments(folder_name):
    res = []
    for inst_path in get_folder_instruments_names(folder_name):
        this_instr = Instrument(instrument_file=inst_path)
        res.append(this_instr)

    return res

def play_all_instruments(in_folder_name : str, output_folder : str):
    instrs = get_folder_instruments_names(in_folder_name)
    for inst in instrs:
        real_instr = Instrument(instrument_file=in_folder_name + "\\" + inst)
        real_instr.play_to_file(output_folder + "\\" + inst[:-len(".instrument")] + ".wav")

def play_file_instrument(filename : str, out_file : str):
    instr = Instrument(music_file=filename, sample_width=2**14, start_sample=0)
    instr.play_to_file(out_file)
    print(instr.harmonics)



if __name__ == '__main__':
    # parse_folder("Notes/Piano", "Instruments/Piano")
    # make_guitar()
    # play_all_instruments("Instruments\\", "Music_res\\")
    play_file_instrument("Music_res/Piano_res.wav", "Music_res/piano_res_res.wav")