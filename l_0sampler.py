#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 00:19:46 2019

@author: devd
"""

import xxhash
import numpy as np
from random import getrandbits, randint, choice
import math
import struct
import sample_streams as strm
import itertools

def is_prime(n):
    """"pre-condition: n is a nonnegative integer
    post-condition: return True if n is prime and False otherwise."""
    if n < 2: 
         return False;
    if n % 2 == 0:             
         return n == 2  # return False
    k = 3
    while k*k <= n:
         if n % k == 0:
             return False
         k += 2
    return True

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
        self.c_check = (self.b*pow(self.r, int(quotient), self.p))
        if quotient == int(quotient) and self.c_check == self.c:
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
            print('a = {} b = {} c = {} a/b = {} r = {} c_check = {}, p = {}'.format(self.a, self.b, self.c, self.a/self.b, self.r, self.c_check, self.p))
            return index, value
        else:
            raise Exception('you tried to sample from subset {} when it hadn\'t been checked successfully'.format(self.i))
    


class l_0_sketch():
    """Warning: only ever sample _ONCE_ from an l_0 sketch.  Taking more samples 
    (ESPECIALLY if you try to subtract the first value you sampled, and then 
    sample again in hopes of getting a second distinct sample) WILL NOT yield
    the desired statistical properties and may actually output nonsense."""
    def __init__(self, n):
        self.n = n
        self.p = self.choose_p()
        #how many times we need to repeat the random processes for high prob of success.  maybe excessive on outer list comp?
        reps = int(math.log2(n))+1
        self.subsets = [[RandomIndexSubset(i, self.p) for i in range(reps)] for j in range(reps)]
# =============================================================================
#         for i in self.subsets:
#             print([j.hasher(50) for j in i])
# =============================================================================
        self.sampled = False
        
    def choose_p(self):
        """p must be prime and also poly(n). i stole this code from stack
        overflow"""
        target = pow(self.n,2)
        while True:
            target += 1
            if is_prime(target):
                break
        return target
    
    def update(self, index, value):
        for mini_sketch in self.subsets:
            for s in mini_sketch:
                s.update(index, value)
    
    def process_stream(self, stream):
        for index, value in stream:
            self.update(index, value)
    
    def check_mini_sketch(self, mini_sketch):
        passes = []
        for subset in mini_sketch:
            if subset.check():
                passes.append(subset.i)
        if passes is not []:
            return passes
        return False
        
        
    def l_0_sample(self):
        if self.sampled:
            raise Exception('You already sampled from this sketch. Sampling again is potentially fatal to you, the user.  Didn\'t you read the docstring?')
        self.sampled = True
        for mini_sketch in self.subsets:
            passed = self.check_mini_sketch(mini_sketch)
            if passed:
                #choose a passing subset in the minisketch at random and get its index/value pair
                index, value = mini_sketch[choice(passed)].sample()
                return index, value
        return False
            
        
        
    
    
    

if __name__ == '__main__':
    n = 1280000
    l = l_0_sketch(n)
    stream = itertools.chain(iter(strm.SampleStream(n)),iter(strm.SampleStream2(n)))
    l.process_stream(stream)
    print('the sampled index, value pair is {}'.format(l.l_0_sample()))
    print('it\'s correct if the index is a multiple of 10 but not 20 and the value is 1')
    