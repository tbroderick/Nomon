#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 15:43:19 2018

@author: TiffMin
"""
import os
import pickle

#If user id is the same, load the click_time_list in the saved file
#Otherwise load empty list
if os.path.exists("data/click_time_log0.0.pickle"):
    with open("data/click_time_log0.0.pickle", 'rb') as temp_handle:
        
        temp_saved_list = pickle.load(temp_handle)
        #saved user id is the 0th element
        click_time_list =temp_saved_list[1]
        user_id = temp_saved_list[0]
        #except:
        #    click_time_list = []