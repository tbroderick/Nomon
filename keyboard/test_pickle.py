#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 19:35:22 2018

@author: TiffMin
"""

import os
import pickle

file_name = "data/preconfig.pickle"
##Add in some try except statements
if os.path.exists(file_name) == False:
    print 'doesnt even exist'
else:
    temp_dens = pickle.load(open("data/preconfig.pickle", 'rb'))
    print "worked till here"
    a = temp_dens[0] 
    print "so does load but no 0th element"