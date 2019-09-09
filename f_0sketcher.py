#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  8 12:59:26 2019

@author: devd
"""

import numpy as np
import xxhash
from random import getrandbits
import math
import struct

class HashFn():
    """Represents a random subset of [n].  Keeps running total of the value of
    all stream updates whose indicies are in this random subset."""
    def __init__(self):
        seed = getrandbits(32)
        self.fn = xxhash.xxh32(seed = seed)
        self.total = 0
        #self.bins = set()
    
    def hasher(self, num):
        """Input: an integer (index for vector).  Output: a random integer."""
        self.fn.reset()
        #self.fn.update(bytes([num]))
        byte_form = struct.pack(">I", num)
        self.fn.update(byte_form)
        return self.fn.intdigest()
    
    def decider(self, index, value, T):
        """Input: index and value of vector update and a T estimate (all 
        integers).  Return yes w/p 1/T by hashing index.  If yes, add value to 
        running total."""
        hashed = self.hasher(index)
        #2^32-1 = 4294967295 is max output value from hash function
        if hashed <= 4294967295/T: 
            self.total = self.total + value
            #self.bins.add(index)
            return True
        return False

def calc_k(eps, delta):
    term1 = -1*np.log(delta)
    term2 = eps/np.power(eps+math.e/3, 2)
    term3 = (1/math.e - eps/3)
    frac = (2+term2)/(term2*eps*term3)
    result = term1*frac
    return result

def T_checker(T, stream, eps, delta, real_k = True, display=False):
    if real_k:
        k = int(calc_k(eps, delta))
    else:
        k = int(np.power(eps, -2) * np.log(np.power(delta,-1)))
    
    hashes = [HashFn() for i in range(k)]
    for index, element in enumerate(stream):
        for h in hashes:
            h.decider(index, element, T)
    nonzeroz = len(list(filter(lambda h: h.total != 0, hashes)))
    threshold = k- k/(math.e)
    if display:
        print("k is {}".format(k))
        print("threshold is {}".format(threshold))
        print("# of nonzeros is {}".format(nonzeroz))
        print("# of zeros is {}".format(k-nonzeroz))
        
        if nonzeroz < threshold:
            print("F_0 < (1-{})T = {} bro. You guessed too high".format(eps, (1-eps)*T))
        else:
            print("F_0 > (1+{})T  = {} superchief.  You guessed too low".format(eps, (1+eps)*T))
        #print([h.total for h in list(filter(lambda h: h.total != 0, hashes))])
        #print([h.total for h in hashes])
        #hash_lengths = 0
        #all_bins = []
        #for h in hashes:
            #hash_lengths = hash_lengths + len(h.bins)
            #all_bins.extend(h.bins)
            #print(h.bins, h.total)
        #for i in range(100):
            #print(i, all_bins.count(i))
    if nonzeroz < threshold:
        return True
    else:
        return False

if __name__ == '__main__':
    #stream = np.identity(10, dtype=int).reshape(100,)
    #T_checker(12, stream, .2, .01, k_wt=1, display=True)
    F_0 = 10
    stream = np.identity((F_0), dtype=int).reshape(F_0**2,)
    T = 12
    if T > F_0:
        too_high = True
    else:
        too_high = False
    real_k = False
    mistakes = 0
    print("testing F_0 = {}, T = {}, real k? {}".format(F_0, T, real_k))
    reps = 100
    for i in range(reps):
        result = T_checker(T, stream, .2, .01, display=False)
        if result != too_high:
            mistakes = mistakes + 1
            print("!", end = '')
        else:
            print(".", end = '')
    print("{}/{} mistakes".format(mistakes, reps))
    