#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 00:19:46 2019

@author: devd
"""

import xxhash
import numpy as np
from random import getrandbits, randint
import math
import struct

class RandomIndexSubset():
    """Represents a random subset of [n] where each element is included 
    independently w/p 1/2^i.  Maintains sum{x_j}, sum{j*x_j}, and 
    sum{x_j*r^j mod p} for all j in the subset.  Set maintained
    in log(n) space via hash functions."""
    def __init__(self, i, p):
        seed = getrandbits(32)
        self.fn = xxhash.xxh32(seed = seed)
        self.total = 0
        self.i = i
        self.threshold = math.pow(2,i)
        #sum{j*x_j}
        self.a = 0
        #sum{x_j}
        self.b = 0
        #sum{x_j*r^j mod p}
        self.c = 0
        self.p = p
        #make sure this randomness works safely, and doesn't, say, give the same
        #output each time you make a new RIS object
        self.r = randint(1, p-1)
        self.queryable = False
    
    def hasher(self, num):
        """Input: an integer (index for vector).  Output: a random integer."""
        self.fn.reset()
        #self.fn.update(bytes([num]))
        byte_form = struct.pack(">I", num)
        self.fn.update(byte_form)
        return self.fn.intdigest()
    
    def update(self, index, value):
        """Input: index and value of vector update.  Return yes w/p 1/2^i by 
        hashing index.  If yes, add value to running totals a,b,c."""
        hashed = self.hasher(index)
        #2^32-1 = 4294967295 is max output value from hash function
        if hashed <= 4294967295/self.threshold: 
            self.a += index * value
            self.b += value
            self.c += value * pow(self.r, index, self.p)
    
    def check(self):
        """Returns True if a,b,c pass the checks. If it does, this indicates
        with probability n/p that the random set contains 1 nonzero entry and
        can be sampled from.  If it fails the checks, no sampling is possible
        and so check returns False."""
        try:
            quotient = self.a/self.b
        except:
            print('b is 0 so it failed.')
            return False
        c_check = (self.b*pow(self.r, int(quotient), self.p))
        if quotient == int(quotient) and c_check == self.c:
            self.queryable = True
            print('passed!')
            return True
# =============================================================================
#         print('didn\'t work.  a = {} b = {} c = {} a/b = {} r = {} c_check = {}'.format(self.a, self.b, self.c, self.a/self.b, self.r, c_check))
#         subset = []
#         for i in range(100):
#             hashed = self.hasher(i)
#             #2^32-1 = 4294967295 is max output value from hash function
#             if hashed <= 4294967295/self.threshold:
#                 subset.append(i)
#         print(subset)
# =============================================================================
        print('failed the checks')
        return False

    def sample(self):
        """If the subset has been checked, return the unique index, value pair
        encoded in a and b."""
        if self.queryable:
            index = int(self.a/self.b)
            value = self.b
            return index, value
        else:
            raise Exception('you tried to sample from subset {} when it hadn\'t been checked successfully'.format(self.i))

if __name__ == '__main__':
    n = 100
    p = pow(n, 3)
    s = RandomIndexSubset(6, p)
    stream = range(50)
    for index, value in enumerate(stream):
        s.update(index, value)
    #s.update(50, 1)
    s.check()
    print(s.sample())
    