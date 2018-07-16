#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 15:43:19 2018

@author: TiffMin
"""
import os
import pickle
import config
import matplotlib.pyplot as plt

#If user id is the same, load the click_time_list in the saved file
#Otherwise load empty list
if os.path.exists("data/click_time_log0.0.pickle"):
    with open("data/click_time_log0.0.pickle", 'rb') as temp_handle:
        try:
            print "hi"
            temp_saved_list = pickle.load(temp_handle)
            #saved user id is the 0th element
            print "yeah"
            click_time_list =temp_saved_list[1]
            print click_time_list
            time_list = [i[0] for i in click_time_list]
            idx_list = [i[1] for i in click_time_list]
            user_id = temp_saved_list[0]
            n_bins = config.num_divs_click
            bins = range(0, config.num_divs_click)
            #plt.plot(temp_saved_list, )
            
            fig, ax = plt.subplots(2,1)
            plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=1)
            ax[0].hist(time_list, bins=n_bins)
            ax[0].set_title("Raw time between clicks")
            ax[0].set_xlabel("seconds")
            ax[0].set_ylabel("count ")
            ax[1].hist(idx_list, bins=bins)
            ax[1].set_title("time index location w.r.t. the top scoring clock")
            ax[1].set_xlabel("bin location relative to noon")
            ax[1].set_ylabel("count")
            plt.show()
            plt.savefig("histogram.jpg")
            
        except:
            click_time_list = []
        
        