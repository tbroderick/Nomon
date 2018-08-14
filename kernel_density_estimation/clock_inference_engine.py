#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 15:28:48 2018

@author: TiffMin
"""

import numpy
import clock_util

class entropy:
    
    def __init__(self, parent):
        self.parent = parent
    
    def init_bits(self, K):
        self.bits_per_select = numpy.log(K) / numpy.log(2)
        return self.bits_per_select
    
    def update_bits(self, K):
        self.bits_per_select = numpy.log(K) / numpy.log(2)
        return self.bits_per_select

class kernel_density_estimation:
    
    def __init__(self):
        pass
    
    #helper functions
    def normal(self, x, mu, sig_sq):
        return numpy.exp(-((x-mu)**2)/(2*sig_sq)) / float(numpy.sqrt(2*numpy.pi*sig_sq))
    
    def optimal_bandwith(self, things):
        n = len(things)
        return 1.06 * (n ** -0.2) * numpy.std(things)

    
    
    def get_past_data(self, data):
        pass
    
    def update_kde(self):
        
class clock_inference(self):
    
    def __init__(self, parent, clockbackend):
        self.parent = parent
    
    self.cscores = 
    self.cur_hours = 
    self.clock_history
    self.entropy = 
    
    
    def update_scores:
        
    def learn_scores:
        
        
    def update_history:
    
    #for only cscores and clock_history
    def init_round:
    
    