'''
This module specialises on keeping and working with music theory concepts
'''


class Tonality:
      tonic = 0
      
      degree_resolution =  {     0: None,
                                 1: (0, 2),
                                 2: None,
                                 3: (2, 4),
                                 4: None,
                                 5: (4, ),      
                                 6: (0, )}
      # odd degrees will resolute into even ones, except unstable 7-th (№6),
      # which resolutes into first

      all_notes_to_letters = {0: 'C',
                    1: 'C#',
                    2: 'D',
                    3: 'D#',
                    4: 'E',
                    5: 'F',
                    6: 'F#',
                    7: 'G',
                    8: 'G#',
                    9: 'A',
                    10: 'A#',
                    11: 'B'}

      all_letters_to_notes = {v: k for k, v in all_notes_to_letters.items()}

      tonality_types = {
                        'major': [0, 2, 4, 5, 7, 9, 11],
                        'minor-harmonic': [0, 2, 3, 5, 7, 8, 11], # most popular minor
                        'minor': [0, 2, 3, 5, 7, 8, 10],
                        }
      
      def __init__(self, tonic = 0, tonality_type = 'major'):
            "Just major or minor + minor-harmonic half support"
            self.tonality_type = tonality_type
            self.tonic = tonic
            self.degrees = self.tonality_types[tonality_type]
                  
            self.real_degrees = [(degr + tonic) for degr in self.degrees]
            self.T = Chord(self, 0)
            self.S = Chord(self, 3)
            self.D = Chord(self, 4)

      def __repr__(self):
            return Tonality.note_to_letter(self.tonic) + '-' + (self.tonality_type)
      
      def degree_to_note(self, degree):
            add = False
            if degree%1 == 0.5:
                  degree -= 0.5
            return self.real_degrees[int(degree)%7] + 12*(degree//7) + add

      def note_to_degree(self, note):
            add = 0
            note -= self.tonic
            if note%12 not in self.degrees:
                  if note%12 - 1 in self.degrees:
                        add = 1
                        note -= 1
                  else:
                        add = -1
                        note += 1
            return self.degrees.index(note%12) + 7*(note//12) + add/2
      
      def check_interval(self, first_note, second_note):
            
            uncompatibility = 0
            
            if first_note not in self.real_degrees:
                  uncompatibility += 10
                  
            if second_note not in self.real_degrees:
                  uncompatibility += 10

            
            if uncompatibility:
                  return uncompatibility

            first_degree  = self.real_degrees.index(first_note)
            second_degree = self.real_degrees.index(second_note)

            
            resolution = self.degree_resolution[first_degree]

                  
            if (resolution is not None and second_degree not in resolution):
                  uncompatibility += 5

            uncompatibility -= (first_degree == 0) + (second_degree == 0)

            return uncompatibility

      def check_melody(self, melody):
            "Looks not only at the notes, but to their resolutions too"
            uncompatibility = 0
            
            melody = [note % 12 for note in melody]
            
            uncompatibility += sum([self.check_interval(*notes_pair)
                                      for notes_pair in adjacent_pairs(melody)])
            
            uncompatibility -= ((melody[0] == self.real_degrees[0])
                                + (melody[-1] == self.real_degrees[0]))*3
            return uncompatibility

      def tonality_disharmony(self, all_notes):
            "Just weights"
            c_rd = np.array(self.real_degrees)
            matrix = np.ones(12)
            matrix[c_rd%12] = 0.5
            matrix[c_rd[[3, 4]]%12] = 0.2 # SD
            matrix[self.tonic] = 0 # T
            return sum(all_notes * matrix)
      
      def note_to_letter(note):
            """
             0  = C
             1  = C#
             2  = D
             3  = D#
             4  = E
             5  = F
             7  = G
             9  = A
             11 = B
             …
            """
            return Tonality.all_notes_to_letters[note%12]
      
      def notes_from_letters(letters):
            return [Tonality.all_letters_to_notes[letter.upper()] for letter in letters.split()]
      
      def notes_to_letters(notes):
            return ' '.join([Tonality.all_notes_to_letters[note%12] for note in notes])


from chord import *
# 
