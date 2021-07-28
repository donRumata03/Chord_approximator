from tonality import *
from chord import *
from melody import *

export_right_chords = True

right = ((['Dm']*4 + ['Gm']*2 + ['A']*2) * 8 + ['Gm', 'A'])*2 + \
        ((['Dm']*4 + ['Gm']*2 + ['A']*2) * 6 + ['Gm', 'A'])*1 + \
        (['Dm']*4 + ['Gm']*2 + ['A']*2) * 8 # right chords for "Кукла колдуна"

assert len(right) == 246

s = Song()

if export_right_chords:
    
    right_melody = '|'.join([ch[0] for ch in right]) # convert to readable string
    s_1 = Song(right_melody, None)

    # copy pauses and length
    s_1.bars_length = s.bars_length
    s_1.delay = s.delay

    # export right chords to file
    # (this is needed to ensure they are right)
    data = s_1.to_audio()
    Player.to_file(data)

# annealing itself
print('ANN started')
import random

def change(dict_, back = False):
    if not back:
        change.changed = random.choice(list(dict_.keys()))
        change.changed_value = (random.random() - 0.5)/5
        dict_[change.changed] += change.changed_value
    else:
        dict_[change.changed] -= change.changed_value

def check_goodness():
    global all_disharmony
    Interval.all_disharmony = all_disharmony
    chords = s.chordify()
    
    return sum([str(bar[0]) == bar[1] for bar in zip(chords, right)])


# just random disharmonies
all_disharmony = {
                    (0, 0): 0,   # prima
                    (1, 1): 4,   # minor second
                    (1, 2): 4,   # major second
                    (1, 3): 4,   # aug second
                    (2, 3): 3,   # minor tercia
                    (2, 4): 3,   # major tercia
                    (3, 4): 4,   # dim quarta
                    (3, 5): 2,   # perf. quarta
                    (3, 6): 3,   # major quarta
                    # ————
                    (4, 6): 3,   # minor quinta 
                    (4, 7): 3,   # perf. quinta
                    (4, 8): 5,   # aug quinta
                    (5, 8): 4,   # minor sexta
                    (5, 9): 4,   # major sexta
                    (6, 9): 5,   # dim septima
                    (6, 10): 4,  # minor septima
                    (6, 11): 4,  # major septima
                    'half-blood': 5, # not in tonality
                    'DS': 5, # DS - penalty
                    'ST': 2, # ST - penalty
                    'SD': -2, # SD - usal
                    'TS': -2 # TS - usual
                   }
# delete!
all_disharmony = Interval.all_disharmony
#

old_goodness = check_goodness()
counter = 10
best = 0
best_dis = None

for _ in range(100_000):
    change(all_disharmony)
    new_goodness = check_goodness()
    if new_goodness < old_goodness:
        print(old_goodness, '->', new_goodness)
        change(all_disharmony, True)
        counter -= 1
        if counter == 0:
            change(all_disharmony)
            old_goodness = check_goodness()
            print('Reverse to', old_goodness)
    else:
        counter = 10
        if new_goodness == old_goodness:
            print(new_goodness)
        else:
            if new_goodness > best:
                best = new_goodness
                best_dis = all_disharmony.copy()
            print(new_goodness, '!')
            old_goodness = new_goodness
print(all_disharmony)
