#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 15:16:11 2018

@author: TiffMin
"""

import pickle, cPickle
import os, sys
import hashlib

class PickleUtil:
    def __init__(self, file_path):
        self.path = file_path
    
    #check that the pickle is in binary
    def is_binary(self):
        pass
    def is_empty(self):
        pass
    #if pickling was interrupted/ pickle file was tampered after save
    #checksum on pickle file to see if it can be safely loaded
    def is_corrupted(self):
        pass
        
    def recover_corrupted(self):
        pass
    def make_binary(self):
        pass
    #load to work in all environments
    def safe_load(self):
        pass
    #safely pickle data
    def safe_save(self):
        pass
        