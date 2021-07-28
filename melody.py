'''
This module specialises on extracting pure data (audio files -> "Song" &
music notation -> "Melody") to objects ("Bar") for further processing, such as
chord detecting
'''

import numpy as np
from tonality import *
from chord import *
import numpy as np


class Bar:
      '''
      In terms of this script, it contains just a set of notes with weights,
      their's length and position don't matter

      It would be better to create "Song bar" and "Melody bar" those extend bar,
      but this is de-facto the same structure, so…
      '''
      
      tonality = Tonality()
      weights = np.array([0]*12)
      melody = None
      
      def __init__(self, data):
            '''Any string input will be considered as melody, other — as just weights'''
            if (type(data[0]) == float or # !!! melody -> data -> weights ?!
                type(data[0]) == int or
                (hasattr(data, 'dtype') and
                 data.dtype.kind in ('fiu')
                 )
                ):
                  self.weights = np.array(data)
                  self.weights = self.weights/max(self.weights) # normalize
            elif type(data[0]) == str:
                  data = Tonality.notes_from_letters(data)
                  for note in data:
                        self.weights[note] += 1
                  self.melody = data
            else:
                 raise ValueError('Bad data input') 
                  
      def sum(*bars):
            
            return Bar(sum(map(lambda b: b.weights, bars)))

      def union(*bars):
            return Bar(' '.join(map(lambda b: Tonality.notes_to_letters(b.melody), bars)))
      
      def __repr__(self):
            
            return str(self.melody) if self.melody else str(self.weights)

      def set_tonality(self, tonality):
            
            self.tonality = tonality

      def get_chord(self, previous_chord = None):
            
            if self.melody is not None:
                  return Chord.detect_best_chord(self.tonality, self.melody, previous_chord)

            return Chord.detect_TSD_by_song(self.tonality, self.weights, previous_chord)
            
      def to_audio(self, duration = 3):
            
            audio = Player.chord(self.get_chord(), duration = duration, volume = 0.15)
            
            if self.melody:
                  audio = Player.sum(audio, Player.union(*[Player.sine_tone(note = m,
                                                                      duration = duration/len(self.melody),
                                                                      volume = 0.4)
                                    for m in self.melody]))
            return audio
      
class Song:
      tempo = 120
      melodic = False
      bars_length = None
      delay = None
      def __init__(self, string = None,
                   file = 'audio_examples/КиШ-караоке.mp3',
                   auto_detect_tonality = True):
            if file:
                  import warnings
                  import librosa
                  print('Imported librosa')
                  with warnings.catch_warnings():
                      warnings.simplefilter("ignore")
                      x, sr = librosa.load(file, sr = None, mono = True)
                  self.duration = librosa.get_duration(x, sr)
                  self.x_harm = librosa.effects.harmonic(x)
                  self.all_chromo = librosa.feature.chroma_stft(self.x_harm, sr = sr)
                  self.tempo, self.beats = librosa.beat.beat_track(x, sr = sr)
                  print('Loaded from librosa')
                  av_chromo = []
                  self.bars_length = []
                  self.delay = self.beats[0] / len(self.all_chromo[0]) * self.duration
                  for i in range(0, len(self.beats) - 2, 2):
                        av_chromo.append(
                              np.average(
                                    self.all_chromo[:, self.beats[i] : self.beats[i+2]],
                                    axis = 1)
                              )
                        self.bars_length.append((self.beats[i+2] - self.beats[i]) / len(self.all_chromo[0]) * self.duration)
                  self.av_chromo = av_chromo
                  self.bars = [Bar(bar) for bar in av_chromo]
            elif string:
                  self.melodic = True
                  bars = string.strip().split('|')
                  self.bars = [Bar(bar) for bar in bars]

            if auto_detect_tonality:
                  self.detect_tonality()
                  
      def detect_tonality(self):
              
            if self.melodic:
                  united_bars = Bar.union(*self.bars)
                  self.all_notes = united_bars.weights
                  print( self.all_notes)
                  self.melody = united_bars.melody
                  all_possible_tonalities = [Tonality(i, tonality_type) for i in range(12)
                                 for tonality_type in Tonality.tonality_types]
                  
                  tonality = min(all_possible_tonalities,
                                    key = lambda tonality: tonality.tonality_disharmony(self.all_notes) + tonality.check_melody(self.melody))
            else:
                  all_possible_tonalities = [Tonality(i, tonality) for i in range(12)
                           for tonality in Tonality.tonality_types]
                  self.all_notes = Bar.sum(*self.bars).weights
                  tonality = min(all_possible_tonalities,
                                 key = lambda tonality: tonality.tonality_disharmony(self.all_notes))
                  
            self.tonality = tonality
            
            for bar in self.bars:
                  bar.set_tonality(tonality)

      def chordify(self):
            
            chords = []
            for bar in self.bars:
                  chords.append(bar.get_chord(previous_chord = chords[-1]
                                              if chords else None))
            return chords
      
      def to_audio(self):
            if not self.bars_length:
                  return Player.union(*[b.to_audio(duration = 60/self.tempo) for b in self.bars])
            else:
                  assert self.delay
                  return Player.union(Player.mute(self.delay), *[b[0].to_audio(duration = b[1]) for b in zip(self.bars, self.bars_length)])
