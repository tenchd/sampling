#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 11:30:37 2019

@author: devd
"""

import abc

class Sketch(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def update():
        """Given an element in a stream, update() performs some linear 
        transformation on the element and adds the result to the sketch."""
    
    @abc.abstractmethod    
    def process_stream(self, stream):
        """Every sketch object processes inputs in the form of a stream.  An
        incremental update is made to the sketch for each element in the 
        stream."""
        for element in stream:
            self.update(element)
        
    @abc.abstractmethod    
    def query():
        """After processing an input stream, querying the sketch will output
        a summary of the sketch state, indicating some property of the input
        defined by the stream (perhaps only approximating the property, or
        returning the correct value with high probability)."""