#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 00:19:46 2019

@author: devd
"""

"""TODO: make hash functions separate from sum state, to allow for composition
of different sketches.  necessary for e.g. graph connectivity where you have
to add node-based sketches with the same randomness together."""

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
    in log(n) space via hash functions. TODO: explain channels in documentation"""
    def __init__(self, i, p, channels):
        seed = getrandbits(32)
        self.fn = xxhash.xxh32(seed = seed)
        self.total = 0
        self.i = i
        self.threshold = math.pow(2,i)
        #sum{j*x_j}
        self.a = np.zeros(channels, dtype=int)
        #sum{x_j}
        self.b = np.zeros(channels, dtype=int)
        #sum{x_j*r^j mod p}
        self.c = np.zeros(channels, dtype=int)
        self.p = p
        #make sure this randomness works safely, and doesn't, say, give the same
        #output each time you make a new RIS object
        self.r = randint(1, p-1)
        self.queryable = [False for j in range(channels)]
        #additionally keep track of linear combos of channels you may have checked
        self.linear_queryable = {}
    
    def hasher(self, num):
        """Input: an integer (index for vector).  Output: a random integer."""
        self.fn.reset()
        #self.fn.update(bytes([num]))
        byte_form = struct.pack(">I", num)
        self.fn.update(byte_form)
        return self.fn.intdigest()
    
    def update(self, index, value, channel):
        """Input: index and value of vector update.  Return yes w/p 1/2^i by 
        hashing index.  If yes, add value to running totals a,b,c."""
        hashed = self.hasher(index)
        #2^32-1 = 4294967295 is max output value from hash function
        if hashed <= 4294967295/self.threshold: 
            self.a[channel] += index * value
            self.b[channel] += value
            self.c[channel] += value * pow(self.r, index, self.p)
    
    def check(self, channel):
        """Returns True if a,b,c pass the checks. If it does, this indicates
        with probability n/p that the random set contains 1 nonzero entry and
        can be sampled from.  If it fails the checks, no sampling is possible
        and so check returns False."""
        #if for some reason you previously checked the sketch on this channel
        #but didn't sample from it, reset the queryable variable (lol) so
        #you don't erroneously pass the check if it should fail.
        self.queryable[channel] = False
        a = self.a[channel]
        b = self.b[channel]
        c = self.c[channel]
        #print('checking i = {} channel = {} a = {} b = {} c = {} a/b = {} r = {} p = {}'.format(self.i, channel, a, b, c, a/b, self.r, self.p))
        try:
            quotient = int(a)/int(b)
        except:
            print('b is 0 so it failed.')
            return False
        self.c_check = (b*pow(self.r, int(quotient), self.p))
        if quotient == int(quotient) and self.c_check == c:
            self.queryable[channel] = True
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

    def sample(self, channel):
        """If the subset has been checked, return the unique index, value pair
        encoded in a and b."""
        if self.queryable[channel]:
            a = self.a[channel]
            b = self.b[channel]
            c = self.c[channel]
            index = int(a/b)
            value = b
            print('a = {} b = {} c = {} a/b = {} r = {} c_check = {}, p = {}'.format(a, b, c, a/b, self.r, self.c_check, self.p))
            return index, value
        else:
            raise Exception('you tried to sample from subset {}, channel {} when it hadn\'t been checked successfully'.format(self.i, channel))
    
# =============================================================================
#     Methods below are for handling sampling from linear combinations of channels
# =============================================================================
    
    def check_linear_combo(self, terms):
        a = 0
        b = 0
        c = 0
        for channel, wt in terms:
            a += wt * self.a[channel]
            b += wt * self.b[channel]
            c += wt * self.c[channel]
        try:
            quotient = int(a)/int(b)
        except:
            print('b is 0 so it failed.')
            return False
        self.c_check = (b*pow(self.r, int(quotient), self.p))
        if quotient == int(quotient) and self.c_check == c:
            self.linear_queryable[terms] = True
            print('passed!')
            return True    
        print('failed the checks')
        return False
    
    def sample_linear_combo(self, terms):
        if self.linear_queryable[terms]:
            a = 0
            b = 0
            c = 0
            for channel, wt in terms:
                a += wt * self.a[channel]
                b += wt * self.b[channel]
                c += wt * self.c[channel]
            index = int(a/b)
            value = b
            print('a = {} b = {} c = {} a/b = {} r = {} c_check = {}, p = {}'.format(a, b, c, a/b, self.r, self.c_check, self.p))
            return index, value
        else:
            raise Exception('you tried to sample from linear combo of channels {} of subset i {} when it hadn\'t been checked successfully'.format(self.terms))
    

class l_0_sketch():
    """Warning: only ever sample _ONCE_ from an l_0 sketch.  Taking more samples 
    (ESPECIALLY if you try to subtract the first value you sampled, and then 
    sample again in hopes of getting a second distinct sample) WILL NOT yield
    the desired statistical properties and may actually output nonsense."""
    def __init__(self, n, channels=1):
        self.n = n
        self.p = self.choose_p()
        #how many times we need to repeat the random processes for high prob of success.  maybe excessive on outer list comp?
        reps = int(math.log2(n))+1
        self.subsets = [[RandomIndexSubset(i, self.p, channels) for i in range(reps)] for j in range(reps)]
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
    
    def update(self, index, value, channel=0):
        for mini_sketch in self.subsets:
            for s in mini_sketch:
                s.update(index, value, channel)
    
    def process_stream(self, stream, channel=0):
        for index, value in stream:
            self.update(index, value, channel)
    
    def check_mini_sketch(self, mini_sketch, channel=0):
        passes = []
        for subset in mini_sketch:
            if subset.check(channel):
                passes.append(subset.i)
        if passes is not []:
            return passes
        return False
        
        
    def l_0_sample(self, channel=0):
        if self.sampled:
            raise Exception('You already sampled from this sketch. Sampling again is potentially fatal to you, the user.  Didn\'t you read the docstring?')
        self.sampled = True
        for mini_sketch in self.subsets:
            passed = self.check_mini_sketch(mini_sketch, channel)
            if passed:
                #choose a passing subset in the minisketch at random and get its index/value pair
                index, value = mini_sketch[choice(passed)].sample(channel)
                return index, value
        return False
    
# =============================================================================
#     Methods below are for handling sampling from linear combinations of channels
# =============================================================================
        
    def check_mini_sketch_linear(self, mini_sketch, terms):
        passes = []
        for subset in mini_sketch:
            if subset.check_linear_combo(terms):
                passes.append(subset.i)
        if passes is not []:
            return passes
        return False
    
    def l_0_sample_linear(self, terms):
        if self.sampled:
            raise Exception('You already sampled from this sketch. Sampling again is potentially fatal to you, the user.  Didn\'t you read the docstring?')
        self.sampled = True
        for mini_sketch in self.subsets:
            passed = self.check_mini_sketch_linear(mini_sketch, terms)
            if passed:
                #choose a passing subset in the minisketch at random and get its index/value pair
                index, value = mini_sketch[choice(passed)].sample_linear_combo(terms)
                return index, value
        return False
            
        
        
    
    
    

if __name__ == '__main__':
    n = 12800
    l = l_0_sketch(n, channels=2)
    #stream = itertools.chain(iter(strm.SampleStream(n)),iter(strm.SampleStream2(n)))
    stream1 = iter(strm.SampleStream(n))
    stream2 = iter(strm.SampleStream2(n))
    l.process_stream(stream1, channel=0)
    l.process_stream(stream2, channel=1)
    terms = ((0,1), (1,1))
    #print('the sampled index, value pair is {}'.format(l.l_0_sample(channel=0)))
    print('the sampled index, value pair is {}'.format(l.l_0_sample_linear(terms)))
    print('it\'s correct if the index is a multiple of 10 but not 20 and the value is 1')
    