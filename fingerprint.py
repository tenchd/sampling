#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 21:36:49 2019

@author: devd
"""

import random
import sample_streams as strm
from sketch_abstract import Sketch
from random import getrandbits

def is_prime(n):
    """"pre-condition: n is a nonnegative integer
    post-condition: return True if n is prime and False otherwise.
    this code stolen from stackoverflow"""
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

def choose_p(n):
        """p must be prime and also poly(n)."""
        target = pow(n,3)
        while True:
            target += 1
            if is_prime(target):
                break
        return target

class Fingerprint_Sketch(Sketch):
    """Maps a length n vector to an integer.  The integer value of the sketch 
    is a fingerprint of the input defined by the stream.  The same input 
    defined by two different streams will sketch to the same fingerprint value.
    For any two different inputs, the probability that they will be sketched 
    to the same fingerprint value is polynomially low."""
    def __init__(self, n, seed=None):
        if seed==None:
            seed=getrandbits(32)
        self.p = choose_p(n)
        random.seed(seed)
        self.r = random.randint(1,self.p-1)
        self.sketch = 0
    
    def update(self, element):
        """Sketches each element in the stream """
        index, value = element
        self.sketch += value * pow(self.r, index, self.p)
        
    def process_stream(self, stream):
        """See super()"""
        super(Fingerprint_Sketch, self).process_stream(stream)
    
    def query(self):
        """Returns the fingerprint of the input stream."""
        return self.sketch


if __name__=='__main__':
    n = 100
    f1 = Fingerprint_Sketch(n)
    f1.process_stream(strm.SampleStream(n))
    f2 = Fingerprint_Sketch(n)
    f2.process_stream(strm.SampleStream2(n))
    print(f1.query(), f2.query())