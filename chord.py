'''
This module realizes basic musical theory objects and some related useful functions,
such as disharmony estimation e.t.c.
'''

from tonality import Tonality
from utility import *
import itertools
from player import *
import fractions

class Interval:
       # optimized values
       # degree_delta, semitone_delta : disharmony level
       # sure that these values can be optimized further
      all_disharmony = {
                  (0, 0): 0.0,                  # prima
                  (1, 1): 4.1445197034783785,   # minor second
                  (1, 2): 5.015715011254885,    # major second
                  (1, 3): 2.3390190911974162,   # aug second
                  (2, 3): 3.1270686720741274,   # minor tercia
                  (2, 4): 2.7497170979169097,   # major tercia
                  (3, 4): 3.3984619546484796,   # dim quarta
                  (3, 5): 1.6167325612201853,   # perf. quarta
                  (3, 6): 2.642123299760769,    # major quarta
                  # ————
                  (4, 6): 3.2118158078948458,   # minor quinta 
                  (4, 7): 3.989974717670634,    # perf. quinta
                  (4, 8): 5.521319985816587,    # aug quinta
                  (5, 8): 3.4750114015645917,   # minor sexta
                  (5, 9): 3.9474972032505713,   # major sexta
                  (6, 9): 4.70546854994258,     # dim septima
                  (6, 10): 4.169059989545495,   # minor septima
                  (6, 11): 3.470306066323917,   # major septima
                  'half-blood': 5.872250458629438,    # not in tonality
                  'DS': 0.4006822972060691,     # DS - penalty
                  'ST': 0.898080460661125,      # ST - penalty
                  'SD': 0.5876216644786547,     # SD - usal
                  'TS': 0.4798890992668126      # TS - usual
                  }

      def __init__(self, tonality,
                   first_note = None,
                   second_note = None,
                   first_degree = None,
                   degree_delta = None):

            assert (first_note is not None) or (first_degree is not None)
            assert (second_note is not None) or (degree_delta is not None)
            
            if first_note is not None:
                  self.first_note = first_note
                  self.first_degree  = tonality.note_to_degree(self.first_note)
            else:
                  self.first_degree = first_degree
                  self.first_note = tonality.degree_to_note(first_degree)
                  
            if second_note is not None:
                  self.second_note = second_note
                  self.second_degree = tonality.note_to_degree(self.second_note)          
            else:
                  self.second_degree = self.first_degree + degree_delta
                  self.second_note   = tonality.degree_to_note(self.second_degree) 
                  
            if self.first_degree > self.second_degree:
                  self.first_degree, self.second_degree = self.second_degree, self.first_degree
                  self.first_note, self.second_note = self.second_note, self.first_note

            self.semitone_delta = self.second_note - self.first_note
            self.degree_delta = self.second_degree - self.first_degree

      def get_disharmony(self):
            add = 0
            
            if self.first_degree%1:
                  add += self.all_disharmony['half-blood']
            if self.second_degree%1:
                  add += self.all_disharmony['half-blood']
            if add:
                  return add
            #try:
            return Interval.all_disharmony[(abs(self.degree_delta%7), abs(self.semitone_delta%12))]
            #except:
             #     print(self.first_note,
             #           self.second_note,
             #           self.first_degree,
             #           self.second_degree,
             #           self.degree_delta,
             #           self.semitone_delta)
             #     return 10
#            fraction = 2**(self.semitone_delta/12)
#            fraction = fractions.Fraction(fraction)
#            rounded = fraction.limit_denominator(14)
#            return float(rounded.denominator + 30*(fraction - rounded)) - 1
      
      def __repr__(self):
            return str(self.degree_delta) + '/' + str(self.semitone_delta)
      
      
class Chord:

      occurrences_by_base_degree = {0: 2,
                                    1: 0,
                                    2: 0,
                                    3: 1,
                                    4: 1,
                                    5: 0,
                                    6: 0}
      classify_chords = {
                              ((2, 4), (2, 3)): '',
                              ((2, 3), (2, 4)): 'm',
                              ((2, 3), (2, 3)): 'dim',
                              ((2, 4), (2, 4)): 'aug',
                        }

      basic_chords = ['', 'm']
      
      def __init__(self, tonality, base_degree, build = None,
                   simplify = True, # TODO
                   **kwargs):
            
            self.tonality = tonality
            self.base_degree = base_degree

            self.build = [0, 2, 4] if build == None else build

            self.degrees = [(base_degree + built_degree)
                            for built_degree in self.build]
            
            self.notes = [tonality.degree_to_note(degree)
                          for degree in self.degrees]

            self.intervals = list(Interval(self.tonality, *note_pair) for note_pair in adjacent_pairs(self.notes))
            self.number_intervals = tuple((interv.degree_delta, interv.semitone_delta) for interv in self.intervals)

            
      def get_disharmony(self, melody_notes, previous_chord = None):
            
            disharmony = []
            for interv in itertools.product(self.notes, melody_notes):
                  r_interv = Interval(self.tonality,
                                   first_note = interv[0], second_note = interv[1]).get_disharmony()
                  
            disharmony = sum(disharmony)
            disharmony -= self.occurrences_by_base_degree[self.base_degree%12]

            if previous_chord:
                  resolution_degree = Tonality.degree_resolution[previous_chord.base_degree%12]
                  if resolution_degree is not None:
                        disharmony += (self.base_degree%12 in resolution_degree)*10
                  
                  disharmony += (previous_chord.base_degree%12 == self.base_degree%12)*3
            else:
                  if self.base_degree%12 != 0:
                        disharmony += 20

            disharmony -= (self.base_degree in [3, 4])*10
            
            return disharmony
      
      def get_disharmony_by_weights(self, weights):
            chord_weights = [2, 1.5, 1]
            disharmony = [Interval(self.tonality,
                                   first_note = interv[0], second_note = interv[1])
                         .get_disharmony() * weights[interv[1]] * chord_weights[self.notes.index(interv[0])]
                         for interv in itertools.product(self.notes, range(12))
                         ]
            disharmony = sum(disharmony)
            return disharmony
      
      def __repr__(self):
            return str(self)
      
      def __str__(self):
            return Tonality.note_to_letter(self.notes[0]) + self.classify()
      
      def classify(self):
            if self.number_intervals in self.classify_chords:
                  return self.classify_chords[self.number_intervals]
            else:
                  print(self.number_intervals)
                  return '?'

      def sort_chords_by_fitness(tonality, melody, previous_chord = None):
            all_possible_chords = [Chord(tonality, degr) for degr in range(7)]
            return sorted(all_possible_chords,
                          key = lambda chord: chord.get_disharmony(melody, previous_chord))
                 
      def detect_best_chord(*args, **kwargs):
            return Chord.sort_chords_by_fitness(*args, **kwargs)[0]
      
      def detect_TSD_by_song(tonality, weights, previous = None):
            possible = [tonality.T, tonality.S, tonality.D]
            disharmonies = [TSD_chord.get_disharmony_by_weights(weights) for TSD_chord in possible]
            if 1:
                  if previous == tonality.D:
                        disharmonies[1] += Interval.all_disharmony['DS'] # DS — bad
                  elif previous == tonality.S:
                        disharmonies[0] += Interval.all_disharmony['ST'] # ST — slightly bad
                        disharmonies[2] -= Interval.all_disharmony['SD'] # SD — ususal combination
                  elif previous == tonality.T:
                        disharmonies[1] -= Interval.all_disharmony['TS'] # TS — usual combination
                        
            return possible[disharmonies.index(min(disharmonies))]

      def to_audio(self, duration = 1):
            return Player.chord(self.notes, duration)
