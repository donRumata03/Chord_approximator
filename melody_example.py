from tonality import *
from chord import *
from melody import *


# melody = [4, 6, 10]

melody = 'F E E D | D F E D | D E F A# A | A F F A# A E'

#melody = 'E F E F|D F E D|A A#'
s = Song(melody, None)
print('tonality', s.tonality)
print(s.chordify())

Player.to_file(s.to_audio())

##
##
##chord = min(all_possible_chords,
##               key = lambda chord: chord.get_disharmony(m3))
##print(chord)
##
##disharmonies = [chord.get_disharmony(m3) for chord in all_possible_chords]
##print(all_possible_chords)
##print(disharmonies)
