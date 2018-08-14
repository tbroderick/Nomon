#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 20:09:26 2018

@author: TiffMin
"""


import os
import cPickle
import sys
sys.path.insert(0, os.path.realpath('../keyboard'))
from pickle_util import *
from nose.tools import assert_equals, assert_raises
#from unittest import assertTrue, assertFalse

    
#create empty pickle file
empty = "test_pickles/empty.pickle"
empty_file = open(empty, 'wb')
empty_file.close()

empty_util = PickleUtil(empty)

# =============================================================================
# #create nonempty but corrupt pickle file
# corrupt = "test_pickles/corrupt.pickle"
# corrupt_file = open(corrupt, 'wb')
# cPickle.dump(['hi', 'hey', 'hello'], corrupt_file) 
# corrupt_file.close()
# 
# 
# corrupt_util = PickleUtil(corrupt)
# 
# =============================================================================
#create non-empty pickle file
nonempty = "test_pickles/nonempty.pickle"
nonempty_file = open(nonempty, 'wb')
cPickle.dump(['hi'], nonempty_file)
nonempty_file.close()

nonempty_util = PickleUtil(nonempty)


#
#Tests for is_empty
#

#Test on is_empty for empty pickle file
def test_is_empty_empty():
    print "Test for whether empty file is empty"
    assert_equals(empty_util.is_empty(), True)

#Test on is_empty for non-empty pickle file
def test_is_empty_nonempty():
    print "Test for whether nonempty file is empty"
    assert_equals(nonempty_util.is_empty(), False)
    
# =============================================================================
# #Test on is_empty for corrupt pickle file
# def test_is_empty_corrupt():
#     print "Test for whether corrupt file is empty"
#     assert_equals(nonempty_util.is_empty(), False)
#     #assert_raises(UnpicklingError, corrupt_util.is_empty)
# 
#     #assert_equals(corrupt_util.is_empty(), False)
#     
# =============================================================================
#    
#Tests for is_corrupt    
#
    
#Test on is_corrupt for empty pickle file
def test_is_corrupt_empty():
    print "Test for whether empty file is corrupt"
    assert_equals(empty_util.is_corrupt(), False)
    
#Test on is_corrupt for empty pickle file
def test_is_corrupt_nonempty():
    print "Test for whether nonempty file is corrupt"
    assert_equals(nonempty_util.is_corrupt(), False)

# =============================================================================
# #Test on is_empty for corrupt pickle file
# def test_is_corrupt_corrupt():
#     print "Test for whether corrupt file is corrupt"
#     assert_equals(corrupt_util.is_corrupt(), True)
# 
# #    
# =============================================================================
#Tests for safe_load    
#


#Test on safe_load for empty pickle file
def test_safe_load_empty():
    print "Test on safe_load for empty pickle file"
    assert_equals(empty_util.safe_load(), None)
    
#Test on safe_load for nonempty pickle file
def test_safe_load_nonempty():
    print "Test on safe_load for nonempty pickle file"
    assert_equals(nonempty_util.safe_load(), ['hi'])
# =============================================================================
# 
# #Test on safe_load for empty pickle file
# def test_safe_load_corrupt():
#     print "Test on safe_load for corrupt pickle file"
#     assert_equals(corrupt_util.safe_load(), None)
# 
# =============================================================================
#    
#Tests for safe_save    
#  
        
#Test on safe_save for list on empty pickle file
def test_safe_save_empty():
    print "Test on safe_save of list on empty pickle file"
    empty_util.safe_save([0,1,2])
    assert_equals(empty_util.safe_load(),[0,1,2])

#Test on safe_save for list on nonempty pickle file
def test_safe_save_nonempty():
    print "Test on safe_save of list on nonempty pickle file"
    nonempty_util.safe_save([0,1,2])
    assert_equals(nonempty_util.safe_load(),[0,1,2])
  
# =============================================================================
# #Test on safe_save for list on nonempty pickle file
# def test_safe_save_corrupt():
#     print "Test on safe_save of list on corrupt pickle file"
#     corrupt_util.safe_save([0,1,2])
#     assert_equals(corrupt_util.safe_load(),[0,1,2])   
#     
# =============================================================================
#Test on safe_save for dictionary
def test_safe_save_dict():
    print "Test on safe_save of dict on nonempty pickle file"
    nonempty_util.safe_save({1:1, 2:2, 3:3})
    assert_equals(nonempty_util.safe_load(),{1:1, 2:2, 3:3})

#Test on Nomon's working pickle files
    
    
    
    

