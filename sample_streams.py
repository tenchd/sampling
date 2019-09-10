#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 17:46:42 2019

@author: devd
"""

class SampleStream():
    """An iterator that generates stream elements to add 1 to every 10th 
    index of the vector"""
    def __init__(self,n):
        self.n = n
        self.i = 0
        
    def __iter__(self):
        return self
  
    def __next__(self):
        if self.i>=self.n:
            raise StopIteration
        else:
            if self.i%100==0:
                print(".", end = '')
            x = self.i
            self.i += 10
            return x,1
        
        
class SampleStream2(SampleStream):
    """An iterator that generates stream elements to subtract 1 from every 20th
    index of the vector"""
    def __next__(self):
        if self.i>=self.n:
            raise StopIteration
        else:
            if self.i%100==0:
                print(".", end = '')                
            x = self.i
            self.i+=20
            return x, -1