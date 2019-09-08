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
    
    def decider(self, num, T):
        """give it a number and a T estimate. it'll return yes w/p 1/T"""
        hashed = self.hasher(num)
        if hashed <= 4294967296/T:
            self.total = self.total + num
            return True
        return False

def T_checker(T, stream, eps, delta):
    #k = O(eps^(-2) log(delta^-1))
    k = int(np.power(eps, -2) * np.log2(np.power(delta,-1)))
    print(k/math.e)
    hashes = [HashFn() for i in range(k)]
    for elt in stream:
        for h in hashes:
            h.decider(elt, T)
    zeroz = len(list(filter(lambda h: h.total == 0, hashes)))
    print(zeroz)
    if zeroz < k/math.e:
        print("it's less than T bro")
    else:
        print("it's more than T superchief")

if __name__ == '__main__':
    #stream = np.ones((20,20), dtype=int).reshape(400,)
    #T_checker(100, stream, .02, .001)
    boy = HashFn()
    count = 0
    for i in range(100000):
        if boy.decider(i, 1):
            count = count + 1
    print(count)
        