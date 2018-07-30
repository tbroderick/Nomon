#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 16:05:24 2018

@author: TiffMin
"""

import sys
import os 
sys.path.insert(0, os.path.realpath('keyboard'))
from pre_broderclocks_pyqt import *
from nose.tools import assert_equals, assertAlmostEqual

##Tests on Pre_HourScoreIncs
phsi = Pre_HourScoreIncs(0,0,2,None)


#Test 
def test_optimal_bandwith1():
    pass

#Test Pre_HourScoreIncs.normal() when x=mu=0.0, std=1.0
def test_normal_1():
    print "Test for normal when x=mu"
    assertAlmostEqual(phsi.normal(0,0,1),0.39894228)
    
#Test Pre_HourScoreIncs.normal() when x=2.0, mu=0.0, std=2.0
def test_normal_2():
    print "Test for normal when x=mu+1std"
    assertAlmostEqual(phsi.normal(2,0,4),0.12098536)

#Test Pre_HourScoreIncs.normal() when x=2.0, mu=0.0, std=2.0
def test_normal_3():
    print "Test for normal when x=mu-std"
    assertAlmostEqual(phsi.normal(-2,0,4),0.12098536)
    

