#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 21:36:49 2019

@author: devd
"""

import random
import sample_streams as strm

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

def fingerprint(n, stream, seed=0):
    """Maps a n-length vector to a random output such that the probability of
    two different vectors mapping to the same output """
    p = choose_p(n)
    random.seed(seed)
    r = random.randint(1, p-1)
    fingerprint = 0
    for index, value in stream:
        fingerprint += value * pow(r, index, p)
    return fingerprint


if __name__=='__main__':
    n = 100
    print(fingerprint(n, strm.SampleStream(n), seed = 3))
    print(fingerprint(n, strm.SampleStream2(n), seed = 3))