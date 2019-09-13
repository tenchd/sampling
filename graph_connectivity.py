#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 21:13:33 2019

@author: devd
"""

import l_0sampler as sktch
import math

def ite(n, index):
    """index to edge.  this is definitely the simplest way to do this"""
    #n = int(0.5*(1 + math.sqrt(8*m+1)))
    m = n*(n-1)/2
    i = n-int(0.5*(1 + math.sqrt(8*(m-index-1)+1)))-1
    j = index + i - int(m-(n-i)*(n-i-1)/2)+1
    print(i,j)
    return i,j
    
class Edge():
    """Wrapper clas for edges, with eti(edge to index) method that calculates
    which indices in the sketch need to be updated when the edge appears in 
    stream."""
    def __init__(self, i, j, insert=True):
        if i==j:
            raise Exception('i and j have to be different')
        self.i, self.j = sorted((i,j))
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

class Supernode():
    """A collection of nodes.  Formed by specifying a particular node or
    merging two (super)nodes."""
    def __init__(self, node = None, nodes = None, parts = None):
        if type(node)==int:
            self.nodes = {node}
        elif type(nodes)==set and nodes:
            self.nodes = nodes
        elif type(parts)==list and parts:
            self.nodes = parts[0].nodes.union(parts[1].nodes)
        else:
            raise Exception("Tried to make a supernode without any nodes to combine")
    
    def display(self):
        print(self.nodes)
    
    def sample(self, sketch):
        if len(self.nodes) == 1:
            (node,) = self.nodes
            sample = sketch.l_0_sample(channel=node)
        else:
            terms = tuple((i,1) for i in self.nodes)
            print('querying {}'.format(terms))
            sample = sketch.l_0_sample_linear(terms)
        if sample==False:
            return False
        index, value = sample
        edge = ite(n,index)
        return edge


class Supernode_Set():
    """maintains invariant: each node is contained by exactly 1 supernode."""
    def __init__(self, n):
        self.n = n
        self.supernodes = {i:Supernode(i) for i in range(n)}
    
    def boruvka_round(self, sketch):
        """Returns False if either no edges between connected components were 
        discovered, or if all nodes are part of the same connected component.  
        True otherwise."""
        edges = []
        #sample an edge incident to each connected component
        for node, cc in self.supernodes.items():
            result = cc.sample(sketch)
            if result != False:
                i,j = result
                e = Edge(i,j)
                edges.append(e)
        #merge connected components based on discovered edges
        for e in edges:
            i,j = e.i, e.j
            a = self.supernodes[i]
            b = self.supernodes[j]
            c = Supernode(parts=[a,b])
            #overwrite previous supernodes a and b
            #BUG HERE SOMEHOW
            for node in c.nodes:
                self.supernodes[i] = c
                
    def display(self):
        for n, cc in self.supernodes.items():
            print(cc.nodes)

def edge_sketcher(m, edge, sketch):
    """Translates an edge update into the signed vertex/edge vector form and
    sends it to the sketch."""
    index = edge.eti(m)
    sketch.update(index, edge.p, channel=edge.i)
    sketch.update(index, -1*edge.p, channel=edge.j)
    




if __name__ == '__main__':
    n = 10
    m = int(n*(n-1)/2)
    rounds = int(math.log2(n))+1
    sketches = [sktch.l_0_sketch(m, channels=10) for r in range(rounds)]
    print(sketches)
    
    edges = [Edge(0,i,insert=True) for i in range(1,10)]
    edges.extend([Edge(0,j,insert=False) for j in range(2,10,2)])
    edges.append(Edge(1,5,insert=True))
    
    for e in edges:
        for sketch in sketches:
            edge_sketcher(n, e, sketch)
    
    
    s = Supernode_Set(n)
    s.display()
    s.boruvka_round(sketches[0])
    s.display()
    s.boruvka_round(sketches[1])
    s.display()