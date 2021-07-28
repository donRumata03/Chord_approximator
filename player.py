'''
This module gives some ways of playing and saving simple music
'''

import numpy as np
from utility import fair_sum
import wave

class Player:
      sample_rate = 4100
      
      def get_freq(note):
            return 440 * 2 ** ((note - 9)/12)

      # out to stream
      def out_audio(data):
            from pyaudio import PyAudio
            if isinstance(data, np.ndarray):
                  data = list(data.astype(int) + 0x80)
            p = PyAudio()
            stream = p.open(format=p.get_format_from_width(1), # 8bit
                           channels=1, # mono
                           rate=Player.sample_rate,
                           output=True)
            stream.write(bytes(data))
            stream.stop_stream()
            stream.close()
            p.terminate()
            
      def sine_tone(duration = 1, volume= 0.2, sample_rate = 4100, note = 0):
            frequency = Player.get_freq(note)
            n_samples = int(sample_rate * duration)
            samples = volume*np.sin(2 * np.pi * frequency * np.arange(n_samples) / sample_rate)* 0x7f

            return samples

      def mute(duration = 1, sample_rate = 4100):
            return np.zeros(int(sample_rate * duration))

      def chord(chord, duration = 1, volume = 0.2):
            return fair_sum([Player.sine_tone(note = note,
                                              duration = duration,
                                              volume = volume)
                             for note in chord.notes])

      def union(*audios):
            return np.concatenate(audios)
      
      def fill_to_length(audio, length):
            return np.concatenate([audio, np.zeros(length - audio.shape[0])])
      
      def sum(*audios):
            length = len(max(audios, key = lambda t: len(t)))
            return fair_sum([Player.fill_to_length(a, length) for a in audios])

      def to_file(data, file = 'out.wav'):
            
            data = np.int8(data + 0x80)
            f = wave.open(file, 'wb')
            f.setnchannels(1)
            f.setsampwidth(1)
            f.setframerate(Player.sample_rate)
            f.writeframes(data.tobytes())
            f.close()



