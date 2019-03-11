#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 15:16:11 2018

@author: TiffMin
"""

import _pickle as cPickle
import os, sys
#import hashlib

class PickleUtil:
    def __init__(self, file_path):
        self.path = file_path
        self.read_output = None
        self.dumped_output = None
        self.read_success = 0
        self.written = 0
    
    def exists(self):
        return os.path.exists(self.path)
    
    
    def is_empty(self):
        if self.exists():
            try:
                cPickle.load(open(self.path, 'rb'))
                #Need to close?
                print(str(self.path) + "all good")
                return False
            except EOFError:
                print(str(self.path) + "not corrupt but empty")
                return True
            except IOError:
                print(str(self.path) + "not empty but can't be opened(corrupt)")
                return False
        else:
            print(str(self.path) + "does not exist")
            return False
    
    def is_corrupt(self):
        if self.exists():
            try:
                cPickle.load(open(self.path, 'rb'))
                #Need to close?
                print(str(self.path) + "all good")
                return False
            except EOFError:
                print(str(self.path) + "not corrupt but empty")
                return False
            #UnpicklingError and IOError
            except:
                print(str(self.path) + "not empty but can't be opened(corrupt)")
                return True
        else:
            print(str(self.path) + "does not exist")
            return False
        
        
         
    #load to work in all environments
    def safe_load(self):
        if self.exists() and not(self.is_empty()) and not(self.is_corrupt()):
            rfile = open(self.path, 'rb')
            self.read_output = cPickle.load(rfile)
            rfile.close()
            self.read_success = 1
        
        else:
            self.read_output = None
        
        
        return self.read_output
            
    #safely pickle data
    def safe_save(self, arg, protocol=2):
        wfile = open(self.path, 'wb')
        self.dumped_output = cPickle.dump(arg, wfile, protocol)
        wfile.close()
        self.written = 1
        
        return self.dumped_output
            
        
    
    #Protocol?
    