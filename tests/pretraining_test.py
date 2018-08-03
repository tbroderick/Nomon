io#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 16:05:24 2018

@author: TiffMin
"""

import os, sys
sys.path.append(os.path.realpath('../keyboard'))
sys.path.append(os.path.realpath('../keyboard/user_preferences'))
from pre_broderclocks_pyqt import *
from nose.tools import assert_equals, assert_almost_equal

##Tests on Pre_HourScoreIncs
phsi = Pre_HourScoreIncs(0,0,2,None)


#
# Tests on Pre_HourScoreIncs.normal()
#
    
#Test Pre_HourScoreIncs.normal() when x=mu=0.0, std=1.0
def test_normal_1():
    print "Test for normal when x=mu"
    assert_almost_equal(phsi.normal(0,0,1),0.39894228)
    
#Test Pre_HourScoreIncs.normal() when x=2.0, mu=0.0, std=2.0
def test_normal_2():
    print "Test for normal when x=mu+1std"
    assert_almost_equal(phsi.normal(2,0,4),0.12098536)

#Test Pre_HourScoreIncs.normal() when x=2.0, mu=0.0, std=2.0
def test_normal_3():
    print "Test for normal when x=mu-std"
    assert_almost_equal(phsi.normal(-2,0,4),0.12098536)

#
# Tests on yin_into_index
#

def test_yin_into_index_1():
    print "Test for yin_into_index when yin in the smallest range"
    assert_equals(phsi.yin_into_index(-0.99),0)

def test_yin_into_index_2():
    print "Test for yin_into_index when yin in the largest range"
    assert_equals(phsi.yin_into_index(0.976),79)

def test_yin_into_index_3():
    print "Test for yin_into_index when yin in the largest range"
    assert_equals(phsi.yin_into_index(0.99), 79)


#
# Tests on index_into_compatible_with_xloc: Maps index 0~79 back to [-1, ..., 0.975]
#

def test_index_into_compatible_with_xloc_1():
    print "Test for index_into_compatible_with_xloc when yin in the smallest range"
    assert_almost_equal(phsi.index_into_compatible_with_xloc(0),-1)

def test_index_into_compatible_with_xloc_2():
    print "Test for index_into_compatible_with_xloc when yin in the second smallest range"
    assert_almost_equal(phsi.index_into_compatible_with_xloc(1), -0.975)

def test_index_into_compatible_with_xloc_3():
    print "Test for index_into_compatible_with_xloc when yin in the largest range"
    assert_almost_equal(phsi.index_into_compatible_with_xloc(79), 0.975)





    