import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
from scipy.io import wavfile
import reader
import numpy

"""

# Number of samplepoints
N = 10000
# sample spacing
T = 1.0 / 800.0
x = np.linspace(0.0, N*T, N)
y = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
yf = scipy.fftpack.fft(y)
xf = np.linspace(0.0, 1.0/(2.0*T), int(N/2))

fig, ax = plt.subplots()
ax.plot(xf, 2.0/N * np.abs(yf[:N//2]))
plt.show()

"""

from pylab import *
from cleaner import *



def f(filename):
    fs, data = wavfile.read(filename) # load the data
    print(fs, max(data.T[0]), type(data[0][0]))
    a = data.T[0] # this is a two channel soundtrack, I get the first track
    b=[(ele/2**16.)*2-1 for ele in a] # this is 8-bit track, b is now normalized on [-1,1)
    c = fft(b) # create a list of complex number
    d = len(c)/2  # you only need half of the fft list
    plt.plot(abs(c[:int(d-1)]),'r')
    plt.show()
    # savefig(filename+'.png',bbox_inches='tight')

def get_fft(for_fft : list, fs : int, to_plot = False):
    fft_res = numpy.fft.rfft(for_fft)
    fft_res = fft_res[:int(len(fft_res) / 2)]
    for i in range(len(fft_res)):
        fft_res[i] = abs(fft_res[i])

    freqs = np.fft.fftfreq(len(for_fft), d = 1 / fs)

    fft_res = fft_res[:int(len(fft_res) / 2)]

    res = [(freqs[i], fft_res[i].real) for i in range(len(fft_res))]


    if to_plot:
        plt.plot([i[0] for i in res], [i[1] for i in res])
        plt.show()
    return res


def get_file_fft(filename : str, sample_size : int, start_sample : int, to_plot = False):
    fs, data = wavfile.read(filename)
    # normalized = reader.normalize_sound(data, 0)
    # for_fft = (normalized.T[0][start_sample:start_sample + sample_size] + normalized.T[1][start_sample:start_sample + sample_size]) / 2
    for_fft = reader.normalize_sound(data[start_sample:start_sample + sample_size], 1)

    return get_fft(for_fft, fs, to_plot)

if __name__ == "__main__":
    get_file_fft("music/guitar_test.wav", 2 ** 14, 74000)
