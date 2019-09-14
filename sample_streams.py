#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 17:46:42 2019

@author: devd
"""

import math

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
            print()
            raise StopIteration
        else:
            if self.i%int(self.n/100)==0:
                print(".", end = '')
            x = self.i
            self.i += 10
            return x,1
        
        
class SampleStream2(SampleStream):
    """An iterator that generates stream elements to subtract 1 from every 20th
    index of the vector"""
    def __next__(self):
        if self.i>=self.n:
            print()
            raise StopIteration
        else:
            if self.i%int(self.n/100)==0:
                print(".", end = '')                
            x = self.i
            self.i+=20
            return x, -1
        
class Edge():
    """Wrapper clas for edges, with eti(edge to index) method that calculates
    which indices in the sketch need to be updated when the edge appears in 
    stream."""
    def __init__(self, endpoints=None, vector=None, insert=True):
        if endpoints is not None:
            i,j = endpoints
            if i==j:
                raise Exception('i and j have to be different')
            self.i, self.j = sorted((i,j))
        elif vector is not None:
            n, index = vector
            self.i, self.j = self.ite(n, index)
        else:
            raise Exception('Edge needs either endpoints or vector form specified')
        if insert:
            self.p = 1
        else:
            self.p = -1
    
    def eti(self, n):
        """Takes a pair i,j and returns the index associated with (i,j)in the 
        length n signed vertex-edge vector."""
        i = self.i
        j = self.j
        index = (i)*n - int((i*(i+1)/2)) + j-i-1
        return int(index)

    def ite(self, n, index):
        """index to edge.  this is definitely the simplest way to do this"""
        #n = int(0.5*(1 + math.sqrt(8*m+1)))
        m = n*(n-1)/2
        i = n-int(0.5*(1 + math.sqrt(8*(m-index-1)+1)))-1
        j = index + i - int(m-(n-i)*(n-i-1)/2)+1
        #print(i,j)
        return i,j

class EdgeStream():
#    def __init__(self, n):
    def __init__(self,n):
        self.n = n
        self.i = 2
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.i >= self.n:
            print()
            raise StopIteration
        else:
            if self.i%int(self.n/100 + 1) == 0:
                print('.', end='')
            e = Edge(endpoints=(self.i%2, self.i))
            self.i+=1
            return e