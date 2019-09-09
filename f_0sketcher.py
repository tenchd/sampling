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



class RandomIndexSubset():
    """Represents a random subset of [n].  Keeps running total of the value of
    all stream updates whose indicies are in this random subset.  Set maintained
    in log(n) space via hash functions."""
    def __init__(self, T):
        seed = getrandbits(32)
        self.fn = xxhash.xxh32(seed = seed)
        self.total = 0
        self.T = T
    
    def hasher(self, num):
        """Input: an integer (index for vector).  Output: a random integer."""
        self.fn.reset()
        #self.fn.update(bytes([num]))
        byte_form = struct.pack(">I", num)
        self.fn.update(byte_form)
        return self.fn.intdigest()
    
    def decider(self, index, value):
        """Input: index and value of vector update and a T estimate (all 
        integers).  Return yes w/p 1/T by hashing index.  If yes, add value to 
        running total."""
        hashed = self.hasher(index)
        #2^32-1 = 4294967295 is max output value from hash function
        if hashed <= 4294967295/self.T: 
            self.total = self.total + value
            return True
        return False

class T_checker():
    """Manages all state required to evaluate whether a particular F_0 estimate
    T is too high or too low over the course of the entire stream."""
    def __init__(self, T, eps, delta, real_k = False, display = False):
        self.T = T
        self.eps = eps
        self.delta = delta
        self.display = display
        #use either true Chernoff-required k or a smaller value
        if real_k:
            self.k = int(self.calc_k(eps, delta))
        else:
            self.k = int(np.power(eps, -2) * np.log(np.power(delta,-1)))
        #make k random subsets for sampling
        self.subsets = [RandomIndexSubset(T) for i in range(self.k)]
        #will report T too high if there are at least k/e empty subsets
        self.threshold = self.k/math.e

    def calc_k(self, eps, delta):
        """Input: epsilon and delta error terms (floats).  Output: k, minimum # of
        random sets required to guarantee multiplicative error factor eps with
        probability of failure no more than delta. Via Chernoff bound argument."""
        term1 = -1*np.log(delta)
        term2 = eps/np.power(eps+math.e/3, 2)
        term3 = (1/math.e - eps/3)
        frac = (2+term2)/(term2*eps*term3)
        result = term1*frac
        return result
    
    def update(self, index, value):
        """Processes a single stream element."""
        for s in self.subsets:
            s.decider(index, value)
        
    def process_stream(self, stream):
        """Processes an entire stream (any iterable containing (index,value)
        pairs)"""
        for index, value in enumerate(stream):
            self.update(index, value)
    
    def evaluate_T(self):
        """Counts the number of empty subsets ("zeros") and returns true if 
        zeros is greater than the threshold.  This indicates that T is too high
        an estimate of F_0.  Otherwise, returns false indicating that T is 
        too low."""
        zeros = len(list(filter(lambda s: s.total==0, self.subsets)))
        if self.display:
            print("k is {}".format(self.k))
            print("threshold is {}".format(self.threshold))
            print("# of zeros is {}".format(zeros))
            
            if zeros > self.threshold:
                print("F_0 < (1-{})T = {} bro. You guessed too high".format(self.eps, (1-self.eps)*T))
            else:
                print("F_0 > (1+{})T  = {} superchief.  You guessed too low".format(self.eps, (1+self.eps)*T))
        if zeros > self.threshold:
            return True
        else:
            return False

# =============================================================================
# def T_checker_old(T, stream, eps, delta, real_k = False, display=False):
#     #use either true Chernoff-required k or a smaller value
#     if real_k:
#         k = int(calc_k(eps, delta))
#     else:
#         k = int(np.power(eps, -2) * np.log(np.power(delta,-1)))
#     
#     subsets = c
#     for index, element in enumerate(stream):
#         for h in subsets:
#             h.decider(index, element)
#     zeroz = len(list(filter(lambda h: h.total == 0, subsets)))
#     threshold = k/(math.e)
#     if display:
#         print("k is {}".format(k))
#         print("threshold is {}".format(threshold))
#         print("# of zeros is {}".format(zeroz))
#         
#         if zeroz > threshold:
#             print("F_0 < (1-{})T = {} bro. You guessed too high".format(eps, (1-eps)*T))
#         else:
#             print("F_0 > (1+{})T  = {} superchief.  You guessed too low".format(eps, (1+eps)*T))
#     if zeroz > threshold:
#         return True
#     else:
#         return False
# =============================================================================


if __name__ == '__main__':
# =============================================================================
#     stream = np.identity(10, dtype=int).reshape(100,)
#     T_checker(12, stream, .2, .01, k_wt=1, display=True)
# =============================================================================
    
    F_0 = 100
    eps = .2
    delta = .01
    stream = np.identity((F_0), dtype=int).reshape(F_0**2,)
    T = 80
    if T > F_0:
        too_high = True
    else:
        too_high = False
    real_k = True
    mistakes = 0
    print("testing F_0 = {}, T = {}, real k? {}".format(F_0, T, real_k))
    reps = 5
    for i in range(reps):
        t = T_checker(T, eps, delta, real_k=real_k, display=False)
        t.process_stream(stream)           
        result = t.evaluate_T()
        if result != too_high:
            mistakes = mistakes + 1
            print("!", end = '')
        else:
            print(".", end = '')
    print("{}/{} mistakes".format(mistakes, reps))
    
# =============================================================================
#     eps = .02
#     n = 1000
#     #print(math.log(1000, 1+eps))
#     #print(math.pow(1.2, 37))
#     #print(math.pow(1.2, 38))
#     length_Ts = int(math.log(n, 1+eps)) + 1
#     Ts = np.unique(np.power(1+eps, np.arange(length_Ts)).astype(int))
#     print(Ts)
# =============================================================================
