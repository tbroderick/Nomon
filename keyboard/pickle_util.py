#!/usr/bin/env python2

######################################
# Copyright 2019 Nicholas Bonaker, Keith Vertanen, Emli-Mari Nel, Tamara Broderick
# This file is part of the Nomon software.
# Nomon is free software: you can redistribute it and/or modify it
# under the terms of the MIT License reproduced below.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY
# OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR
#OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# <https://opensource.org/licenses/mit-license.html>
######################################


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
                # print(str(self.path) + " all good")
                return False
            except EOFError:
                print(str(self.path) + " not corrupt but empty")
                return True
            except IOError:
                print(str(self.path) + " not empty but can't be opened(corrupt)")
                return False
        else:
            print(str(self.path) + " does not exist")
            return False
    
    def is_corrupt(self):
        if self.exists():
            try:
                cPickle.load(open(self.path, 'rb'))
                #Need to close?
                # print(str(self.path) + "all good")
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
    