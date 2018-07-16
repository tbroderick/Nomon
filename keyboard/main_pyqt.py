#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 18:41:38 2018

@author: TiffMin
"""

import keyboard_pre_pyqt
import keyboard
import os
import pickle

file_name = "preconfig.pickle"
##Add in some try except statements
if os.path.exists(file_name) == False:
    keyboard_pre_pyqt.main()
    keyboard.main()
    #if :
    #    keyboard.main()
        
else:
    try:
        with open("preconfig.pickle", 'rb') as handle:
            temp_dens = pickle.load(handle)
        if temp_dens[1] >0 and temp_dens[2] >0 and len(temp_dens[0])> 0:
            keyboard.main()
        else:
            keyboard_pre_pyqt.main()
    except:
        keyboard.main()
        