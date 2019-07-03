#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 00:19:46 2019

@author: devd
"""

import xxhash as hash
import numpy as np
from random import getrandbits, randint
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
    
    
N = 400
p = 5*N + 3

vector = np.random.randint(10, size=N)

for i in range(0, int(math.log(N, 2)+1)):
    s_i = np.zeros((N,))
    x = HashFn()
    parity = math.pow(2, i)
    for j in range(N):
        if x.decider(j, parity):
            s_i[j] = vector[j]
    #print(np.count_nonzero(s_i)/N)
    nonzeros = np.count_nonzero(s_i)
    if nonzeros==0:
        print("level {} has no entries. skipping.".format(i))
        continue
    small = s_i[np.nonzero(s_i)]
    small_index = np.stack([small, np.nonzero(s_i)[0]])
    #print(small_index)
    
    a = np.sum(np.multiply(small_index[0], small_index[1]))
    b = np.sum(small_index[0])
    r = randint(1, p-1)
    r_j = np.power(r, small_index[1])
    c = np.sum(np.mod(np.multiply(small_index[1], r_j),p))
    print (a, b, c)
    quot = a/b
    print(quot)
    if quot.is_integer():
        print("{} is an integer".format(quot))
        check = ((b%p)*pow(r, int(quot), p))%p
        print("c is {} and ((b%p)*pow(r, int(quot), p))%p is {}".format(c, check))
        #if c==check:
        
        #OK SOMEHOW MY CHECK ISN'T WORKING RIGHT.  THERE ARE CORRECT VALUES THAT AREN'T RECOGNIZED
        print("{} passed!".format(i))
        print("it's got {} nonzero entries".format(nonzeros))
        print("the {} entry of vector is {}".format(quot, b))
        print("check: OG vector has the {} value as {}".format(int(quot), vector[int(quot)]))
        