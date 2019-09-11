#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 21:13:33 2019

@author: devd
"""

class Edge():
    """Wrapper clas for edges, with eti(edge to index) method that calculates
    which indices in the sketch need to be updated when the edge appears in 
    stream."""
    def __init__(self, i, j, insert):
        self.i, self.j = sorted(i,j)
        if insert:
            self.p = 1
        else:
            self.p = 0
    
    def eti(self, n):
        """Takes a pair i,j and returns the index associated with (i,j)in the 
        length n signed vertex-edge vector."""
        i = self.i
        j = self.j
        index = (i)*n - int((i*(i+1)/2)) + j-i-1
        return index

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
    

def edge_sketcher(n, edge, sketch):
    """Translates an edge update into the signed vertex/edge vector form and
    sends it to the sketch."""
    index = edge.eti(n)
    sketch.update(index, 1*edge.p, edge.i)
    sketch.update(index, -1*edge.p, edge.j)



if __name__ == '__main__':
    a = Supernode(node=0)
    b = Supernode(node=1)
    c = Supernode(parts=[a,b])
    c.display()
    d = Supernode(node=3)
    e = Supernode(parts=[c,d])
    e.display()