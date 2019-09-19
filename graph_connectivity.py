#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 21:13:33 2019

@author: devd
"""

import l_0sampler as sktch
import math
from sample_streams import Edge, EdgeStream


    

class Supernode():
    """A collection of nodes.  Formed by specifying a particular node, or set 
    of nodes, or merging two (super)nodes."""
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
        """Print out current set of nodes in the supernode."""
        print(self.nodes)
    
    def sample(self, sketch):
        """Samples an outgoing edge from the supernode from the given sketch."""
        if len(self.nodes) == 1:
            (node,) = self.nodes
            sample = sketch.query(channel=node)
        else:
            terms = tuple((i,1) for i in self.nodes)
            sample = sketch.query(linear=True,terms=terms)
        if sample==False:
            return False
        index, value = sample
        edge = Edge(vector = (n,index))
        return edge


class Supernode_Set():
    """maintains invariant: each node is contained by exactly 1 supernode."""
    def __init__(self, n):
        self.n = n
        self.supernodes = {i:Supernode(i) for i in range(n)}
    
    def boruvka_round(self, sketch):
        """Returns True if either no edges between connected components were 
        discovered, or if all nodes are part of the same connected component.  
        False otherwise."""
        edges = set()
        change = False
        #sample an edge incident to each connected component
        #need to loop over only unique ccs
        for cc in set(cc for cc in self.supernodes.values()):
            #print('looking for an edge out of {}'.format(cc.nodes))
            result = cc.sample(sketch)
            if result != False:
                #print(result)
                change = True
                #i,j = result
                #e = Edge(i,j)
                edges.add(result)
        if not change:
            return True
        #merge connected components based on discovered edges
        for e in edges:
            i,j = e.i, e.j
            #print('combining {} and {}'.format(self.supernodes[i].nodes, self.supernodes[j].nodes))
            a = self.supernodes[i]
            b = self.supernodes[j]
            c = Supernode(parts=[a,b])
            #overwrite previous supernodes a and b
            for node in c.nodes:
                self.supernodes[node] = c
        if len(self.supernodes[0].nodes)==n:
            return True
        return False
                
    def display(self):
        print('displaying supernode set')
        for n, cc in self.supernodes.items():
            print(n, cc.nodes)
            
    def get_ccs(self):
        ccs = set(self.supernodes.values())
        return [cc.nodes for cc in ccs]

def edge_sketcher(m, edge, sketch):
    """Translates an edge update into the signed vertex/edge vector form and
    sends it to the sketch."""
    index = edge.eti(m)
    sketch.update(index, edge.p, channel=edge.i)
    sketch.update(index, -1*edge.p, channel=edge.j)
    
def graph_connectivity(n, edge_stream):
    m = int(n*(n-1)/2)
    rounds = int(math.log2(n))+1
    sketches = [sktch.l_0_sketch(m, channels=n) for r in range(rounds)]
    for e in edge_stream:
        for sketch in sketches:
            edge_sketcher(n, e, sketch)
    s = Supernode_Set(n)
    #s.display()
    done = False
    b_round = 0
    while not done:
        done = s.boruvka_round(sketches[b_round])
        #print('Are we done yet? {}'.format(done))
        b_round += 1
        #s.display()
    return s.get_ccs()


if __name__ == '__main__':
    n = 100
    
    edges = EdgeStream(n)
    #edges = [Edge(endpoints = (0,i), insert=True) for i in range(1,10)]
    #edges.extend([Edge(endpoints = (0,j), insert=False) for j in range(2,10,2)])
    #edges.extend([Edge(endpoints=(3,k),insert=True) for k in range(4,10,2)])
    
    for cc in graph_connectivity(n, edges):
        print(len(cc))
    
