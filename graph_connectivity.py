#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 21:13:33 2019

@author: devd
"""

import l_0sampler as sktch
import math

def ite(m, index):
    """index to edge.  this is definitely the simplest way to do this"""
    n = int(0.5*(1 + math.sqrt(8*m+1)))
    i = n-int(0.5*(1 + math.sqrt(8*(m-index-1)+1)))-1
    j = index + i - int(m-(n-i)*(n-i-1)/2)+1
    return i,j
    
class Edge():
    """Wrapper clas for edges, with eti(edge to index) method that calculates
    which indices in the sketch need to be updated when the edge appears in 
    stream."""
    def __init__(self, i, j, insert):
        if i==j:
            raise Exception('i and j have to be different')
        self.i, self.j = sorted((i,j))
        if insert:
            self.p = 1
        else:
            self.p = -1
    
    def eti(self, m):
        """Takes a pair i,j and returns the index associated with (i,j)in the 
        length n signed vertex-edge vector."""
        i = self.i
        j = self.j
        index = (i)*m - int((i*(i+1)/2)) + j-i-1
        return int(index)

class Supernode():
    """A collection of nodes.  Formed by specifying a particular node or
    merging two (super)nodes."""
    def __init__(self, node = None, parts = None):
        if type(node)==int:
            self.nodes = {node}
        elif type(parts)==list and parts:
            self.nodes = parts[0].nodes.union(parts[1].nodes)
        else:
            raise Exception("Tried to make a supernode without any nodes to combine")
    
    def display(self):
        print(self.nodes)
    

def edge_sketcher(m, edge, sketch):
    """Translates an edge update into the signed vertex/edge vector form and
    sends it to the sketch."""
    index = edge.eti(m)
    sketch.update(index, edge.p, channel=edge.i)
    sketch.update(index, -1*edge.p, channel=edge.j)



if __name__ == '__main__':
    n = 10
    m = int(n*(n-1)/2)
    sketch = sktch.l_0_sketch(m, channels=10)
    edges = [Edge(0,i,insert=True) for i in range(1,10)]
    edges.extend([Edge(0,j,insert=False) for j in range(2,10,2)])
    for e in edges:
        edge_sketcher(m, e, sketch)
    terms = ((0,1),(1,1),(5,1),(7,1),(9,1))
    sample=sketch.l_0_sample_linear(terms)
    index, value = sample
    print(ite(m, index))