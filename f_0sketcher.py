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
import itertools



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
    def __init__(self, T, eps, delta, k, display = False):
        self.T = T
        self.eps = eps
        self.delta = delta
        self.display = display
        self.k = k
        
        #make k random subsets for sampling
        self.subsets = [RandomIndexSubset(T) for i in range(self.k)]
        #will report T too high if there are at least k/e empty subsets
        self.threshold = self.k/math.e
    
    def update(self, index, value):
        """Processes a single stream element."""
        for s in self.subsets:
            s.decider(index, value)
        
    def process_stream(self, stream):
        """Processes an entire stream (any iterable containing (index,value)
        pairs)"""
        for index, value in stream:
            self.update(index, value)
    
    def evaluate_T(self):
        """Counts the number of empty subsets ("zeros") and returns true if 
        zeros is greater than the threshold.  This indicates that T is too high
        an estimate of F_0.  Otherwise, returns false indicating that T is 
        too low."""
        #print(self.subsets)
        zeros = len(list(filter(lambda s: s.total==0, self.subsets)))
        if self.display:
            print("k is {}".format(self.k))
            print("threshold is {}".format(self.threshold))
            print("# of zeros is {}".format(zeros))
            
            if zeros > self.threshold:
                print("F_0 < (1-{})T = {} bro. You guessed too high".format(self.eps, (1-self.eps)*self.T))
            else:
                print("F_0 > (1+{})T  = {} superchief.  You guessed too low".format(self.eps, (1+self.eps)*self.T))
        if zeros > self.threshold:
            return True
        else:
            return False

class F_0_sketcher():
    """Top-level class for F_0 sketcher."""
    def __init__(self, n, stream, eps, delta, real_k=False, display=False):
        self.n =n
        self.stream = stream
        self.eps = eps
        self.delta = delta
        
        #use either true Chernoff-required k or a smaller value
        if real_k:
            self.k = int(self.calc_k(eps, delta))
        else:
            self.k = int(np.power(eps, -2) * np.log(np.power(delta,-1)))
        
        length_Ts = int(math.log(n, 1+eps)) + 2
        #create a list of (1+eps)^i T value estimates 
        T_vals = np.unique(np.power(1+eps, np.arange(length_Ts)).astype(int))
        T_vals[-1] = n
        #create the sketch objects for each T estimate
        self.Ts = [T_checker(t, eps, delta, self.k, display) for t in T_vals]

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
        
    def process_stream(self):
        """Iterates through the stream iterator, applying each stream element
        to each of the T-estimate sketches"""
        for index, value in self.stream:
            for t in self.Ts:
                t.update(index, value)
    
    def estimate_F_0(self):
        """Call this after the stream has been processed to get an estimate
        for F_0.  At the moment it assumes the lowest T-estimate to have a 
        sketch that evaluates to True is the best estimate.  Since any of the
        T-estimate sketches can fail and give the wrong answer, this can be
        wrong when a T-estimate sketch with T< F_0 fails.  Fix it"""
        #this part assumes that you switch from F to T once and it never changes
        #again.  needs to be fixed!
        for t in self.Ts:
            if t.evaluate_T():
                return t.T

class SampleStream():
    """An iterator that generates stream elements to add 1 to every 10th 
    index of the vector"""
    def __init__(self,n):
        self.n = n
        self.i = 0
        
    def __iter__(self):
        return self
  
    def __next__(self):
        if self.i==self.n:
            raise StopIteration
        else:
            x = self.i
            self.i += 10
            return x,1
        
class SampleStream2(SampleStream):
    """An iterator that generates stream elements to subtract 1 from every 20th
    index of the vector"""
    def __next__(self):
        if self.i==self.n:
            raise StopIteration
        else:
            x = self.i
            self.i+=20
            return x, -1
            

if __name__ == '__main__':
    
    n = 10000
    eps = .1
    delta = .01
    stream = itertools.chain(iter(SampleStream(n)),iter(SampleStream2(n)))
    #stream = iter(SampleStream(n))
    f = F_0_sketcher(n, stream, eps, delta, real_k = False)
    f.process_stream()
    print(f.estimate_F_0())
    
    
# =============================================================================
#     
#     F_0 = 100
#     eps = .2
#     delta = .01
#     stream = np.identity((F_0), dtype=int).reshape(F_0**2,)
#     T = 80
#     if T > F_0:
#         too_high = True
#     else:
#         too_high = False
#     real_k = True
#     mistakes = 0
#     print("testing F_0 = {}, T = {}, real k? {}".format(F_0, T, real_k))
#     reps = 5
#     for i in range(reps):
#         t = T_checker(T, eps, delta, real_k=real_k, display=False)
#         t.process_stream(stream)           
#         result = t.evaluate_T()
#         if result != too_high:
#             mistakes = mistakes + 1
#             print("!", end = '')
#         else:
#             print(".", end = '')
#     print("{}/{} mistakes".format(mistakes, reps))
# =============================================================================
