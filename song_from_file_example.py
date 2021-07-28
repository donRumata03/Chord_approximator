from tonality import *
from chord import *
from melody import *


s = Song(file = 'audio_examples/Какое сегодня число.mp3')

print('tonality', s.tonality)
print(s.chordify())

#Player.out_audio(s.to_audio())
data = s.to_audio()
Player.to_file(data)
