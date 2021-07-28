'''
Just few useful functions
'''
from functools import reduce

def adjacent_pairs(list_):
      for i in range(len(list_) - 1):
            yield list_[i], list_[i+1]

def adjacent_pairs_diff(list_):
      return map(lambda t: t[1] - t[0], adjacent_pairs(list_))

def fair_sum(list_):
      return reduce(lambda a,b: a + b, list_)
