import json
import math
import os
import sys
import wave
import numpy as np
from matplotlib import pyplot as plt
from scipy.io import wavfile
import scipy.fftpack

sample_width_types = {
    1: np.int8,
    2: np.int16,
    4: np.int32
}

raws = None

def get_wav_data(filename) -> tuple:
    global raws
    wav = wave.open(filename, "r")

    (channels_num, sample_width, framerate, frames_num, compression_type, compression_name) = wav.getparams()
    content = wav.readframes(frames_num)
    raws = content
    print((channels_num, sample_width, framerate, frames_num, compression_type, compression_name))
    duration = frames_num / framerate
    peak = 256 ** sample_width / 2

    sample_type = sample_width_types[sample_width]

    channels_raw_data = []
    samples = []


    for this_channel in range(channels_num):
        channels_raw_data.append(content[this_channel::channels_num])
        samples.append([])
        for sample_index in range(int(frames_num / sample_width)):
            sample = channels_raw_data[-1][sample_index * sample_width : (sample_index + 1) * sample_width]
            # print(sample, np.frombuffer(sample, dtype = sample_type))
            samples[-1].append(int(np.frombuffer(sample, dtype = sample_type)[0]))

    return framerate, frames_num, duration, samples

def save_file(samples, filename, framerate, sample_width = 2) -> None:
    num_channels = len(samples)
    raw_bytes = bytearray()
    for index in range(len(samples[0])):
        for channel in range(num_channels):
            this_bytes = samples[channel][index].to_bytes(sample_width, byteorder='big', signed = True)
            for byte in this_bytes:
                raw_bytes.append(byte)
    # .to_bytes(sample_width, byteorder='big', signed = True)


    print(len(raw_bytes))
    raw_bytes = bytes(raw_bytes)
    print(len(raw_bytes))

    print(memoryview(raw_bytes[:100]).hex(), "\n\n", memoryview(raws[:100]).hex())

    file = wave.open(filename, "wb")
    file.setframerate(framerate)
    file.setsampwidth(sample_width)
    file.setnchannels(num_channels)
    file.setnframes(int(len(raw_bytes) / num_channels))
    # file.setparams((num_channels, sample_width, framerate, int(len(raw_bytes) / sample_width), "NONE", "No compression"))
    file.writeframesraw(raw_bytes)
    file.close()

    """
    file = open(filename, mode = "rb")
    buff = file.read()
    file.close()

    file = open(filename, "wb")
    file.write(buff + raw_bytes)
    file.close()
    """


def plot_wave(samples):
    plt.plot(list(range(len(samples))), samples)
    plt.show()

def sc_wav_open(filename):
    fs, data = wavfile.read(filename)
    res = data.T[0][100:2148]

    yf = scipy.fftpack.fft(res)
    print(len(yf))
    xf = np.linspace(0, 20000, len(yf))

    plt.plot(xf, yf)

    # plt.plot(xf, 2.0 / len(xf) * np.abs(yf[:len(xf) // 2]))
    """
    fig, ax = plt.subplots()
    ax.plot(xf, 2.0 / len() * np.abs(yf[:N // 2]))
    """
    plt.show()


def my_open_file(filename):
    os.system("Kostil.exe " + filename + " temp.json")
    all_data = json.loads((open("temp.json", "r").read()))

    data = all_data["data"][0][::100]
    sample_rate = all_data["sample_rate"]
    print(len(data))

    to_plt_x = []
    to_plt_y = []

    for i in range(len(data)):
        to_plt_x.append(i / sample_rate)
        to_plt_y.append(data[i])

    plt.plot(to_plt_x, to_plt_y)
    plt.show()


def normalize_sound(samples : np.ndarray, mode = 1): # Linear (1, default) or raw (0)
    div = 1
    el = 0
    if len(samples.shape) == 1:
        el = samples[0]
    else:
        el = samples[0][0]
    if type(el) == np.int8:
        div = 2 ** 8
    elif type(el) == np.int16:
        div = 2 ** 16
    elif type(el) == np.int32:
        div = 2 ** 32

    res = None
    linear_res = []

    if len(samples.shape) != 1:
        res = np.ndarray((len(samples), len(samples[0])), dtype = np.float)

        for i1, val in enumerate(samples):
            this_sum = 0
            for i2, val_val in enumerate(val):
                res[i1][i2] = val_val / div
                # this_sum += val_val / div
            # linear_res.append(sum(res[i1]) / len(val))
            # print(sum(res[i1]), len(val), sum(res[i1]) / len(val))

    else:
        res = np.ndarray((len(samples),), dtype = np.float)
        for i in range(len(samples)):
            res[i] = samples[i] / div

        return res

    # plt.plot(list(range(len(linear_res))), linear_res)
    # plt.show()

    linear_res = np.ndarray((res.shape[0],))

    T = res.T

    for i in range(len(T)):
        linear_res += T[i]
    linear_res /= len(T)

    return res if mode == 0 else linear_res

if __name__ == "__main__":
    filename = "music/guitar_test.wav"
    sc_wav_open(filename)
    # data = get_wav_data(filename)[3][0][::100]
    # my_open_file(filename)
    # plot_wave(data)
