#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 21:13:33 2019

@author: devd
"""


def eti(n, i, j):
    """Takes an edge i,j and returns the index associated with (i,j)in the 
    length n signed vertex-edge vector."""
    index = (i)*n - int((i*(i+1)/2)) + j-i-1
    return index

def edge_sketcher(n, edge, sketch):
    """Translates an edge update into the signed vertex/edge vector form and
    sends it to the sketch."""
    i,j = sorted(edge)
    index = eti(n,i,j)
    sketch.update(index, 1, i)
    sketch.update(index, -1, j)