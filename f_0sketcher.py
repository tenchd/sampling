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

def T_checker(T, stream, eps, delta):
    #k = O(eps^(-2) log(delta^-1))
    k = int(np.power(eps, -2) * np.log(np.power(delta,-1)))
    print(k/math.e)
    hashes = [HashFn() for i in range(k)]
    for index, element in enumerate(stream):
        for h in hashes:
            h.decider(index, element, T)
    nonzeroz = len(list(filter(lambda h: h.total != 0, hashes)))
    print(nonzeroz)
    if nonzeroz < k/math.e:
        print("F_0 < (1-{})T = {} bro".format(eps, (1-eps)*T))
    else:
        print("F_0 > (1+{})T  = {} superchief".format(eps, (1+eps)*T))
   # print([h.total for h in hashes])

if __name__ == '__main__':
    stream = np.identity((100), dtype=int).reshape(10000,)
    T_checker(200, stream, .2, .1)
    