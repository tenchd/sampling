#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 18:14:46 2019

@author: devd
"""

from random import getrandbits
import xxhash
import math
import struct
from sketch_abstract import Sketch

class Hash():
    def __init__(self, choices, seed=None):
        if seed==None:
            seed = getrandbits(32)
        self.fn = xxhash.xxh32(seed = seed)
        self.choices = choices
    
    def hasher(self, num):
        """Input: an integer (index for vector).  Output: a random integer."""
        self.fn.reset()
        #self.fn.update(bytes([num]))
        byte_form = struct.pack(">I", num)
        self.fn.update(byte_form)
        return self.fn.intdigest()
    
    def choose_bit(self, element):
        bit = self.hasher(element)%self.choices
        return bit

class BloomFilter():
    def __init__(self, n, m):
        self.n = n
        self.m = m
        self.k = int(m/n * math.log(2))
        self.hashes = [Hash(self.m) for i in range(self.k)]
        self.filter = [0 for i in range(m)]
    
    def add_to_filter(self, element):
        """Adds integer element to the bloom filter."""
        for h in self.hashes:
            index = h.choose_bit(element)
            self.filter[index] = 1
    
    def populate_filter(self, elements):
        for element in elements:
            self.add_to_filter(element)
        
    def test_against_filter(self, item):
        for h in self.hashes:
            index = h.choose_bit(item)
            if self.filter[index] == 0:
                return False
        return True
    

if __name__ == '__main__':
    b = BloomFilter(n=10, m=200)
    for i in range(0,150, 15):
        b.add_to_filter(i)
    for i in range(200):
        if b.test_against_filter(i):
            print(i)