#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 00:19:46 2019

@author: devd
"""

import xxhash as hash
import numpy as np
from random import getrandbits
import math
import struct

class HashFn():
    """wrapper class for xxhash objects"""
    def __init__(self):
        seed = getrandbits(32)
        self.fn = hash.xxh32(seed = seed)
    
    def hasher(self, num):
        """give it a number (index for vector), it returns a random integer"""
        self.fn.reset()
        #self.fn.update(bytes([num]))
        byte_form = struct.pack(">I", num)
        self.fn.update(byte_form)
        return self.fn.intdigest()
    
    def decider(self, num, parity):
        """give it a number and an S index. it'll return whether the number
        belongs in S_index"""
        hashed = self.hasher(num)
        if hashed%parity == 0:
            return True
        return False
    
    
N = 4000

vector = np.random.randint(0, 1000, (N,))

for i in range(0, int(math.log(N, 2))):
    s_i = np.zeros((N,))
    x = HashFn()
    parity = math.pow(2, i)
    for j in range(N):
        if x.decider(j, parity):
            s_i[j] = vector[j]
    print(np.count_nonzero(s_i)/N)
        

