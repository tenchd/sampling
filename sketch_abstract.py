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
        """"""
    
    @abc.abstractmethod    
    def process_stream(self, stream):
        for element in stream:
            self.update(element)
        
    @abc.abstractmethod    
    def query():
        """"""