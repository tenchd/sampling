# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import xxhash
from random import getrandbits, randint
import math
import struct

class HashFn():
    """wrapper class for xxhash objects"""
    def __init__(self):
        seed = getrandbits(32)
        self.fn = xxhash.xxh32(seed = seed)
        self.total = 0
    
    def hasher(self, num):
        """give it a number (index for vector), it returns a random integer"""
        self.fn.reset()
        #self.fn.update(bytes([num]))
        byte_form = struct.pack(">I", num)
        self.fn.update(byte_form)
        return self.fn.intdigest()
    
    def decider(self, index, value, T):
        """give it a number and a T estimate. it'll return yes w/p 1/T"""
        hashed = self.hasher(index)
        if hashed <= 4294967296/T:
            self.total = self.total + value
            return True
        return False

def T_checker(T, stream, eps, delta, k_wt=1, display=False):
    #k = O(eps^(-2) log(delta^-1))
    k = int(k_wt * np.power(eps, -2) * np.log(np.power(delta,-1)))
    hashes = [HashFn() for i in range(k)]
    for index, element in enumerate(stream):
        for h in hashes:
            h.decider(index, element, T)
    nonzeroz = len(list(filter(lambda h: h.total != 0, hashes)))
    if display:
        print(k/math.e)
        print(nonzeroz)
        if nonzeroz < k/math.e:
            print("F_0 < (1-{})T = {} bro. You guessed too high".format(eps, (1-eps)*T))
        else:
            print("F_0 > (1+{})T  = {} superchief.  You guessed too low".format(eps, (1+eps)*T))
    if nonzeroz < k/math.e:
        return True
    else:
        return False

if __name__ == '__main__':
    F_0 = 100
    stream = np.identity((F_0), dtype=int).reshape(F_0**2,)
    T = 150
    ks = [1, 1/2, 1/5, 1/10, 1/20]
    if T > F_0:
        too_high = True
    else:
        too_high = False

    for k in ks:
        mistakes = 0
        print("testing F_0 = {}, T = {}, k factor = {}".format(F_0, T, k))
        reps = 100
        for i in range(reps):
            print(".", end = '')
            result = T_checker(T, stream, .2, .01, k_wt=k, display=False)
            if result != too_high:
                mistakes = mistakes + 1
        print("{}/{} mistakes".format(mistakes, reps))
    