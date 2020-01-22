#!/usr/bin/python

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


import numpy as np
import pickle
import os, sys
#sys.path.insert(0, os.path.realpath('user_preferences'))
current_folder= os.path.dirname(os.path.abspath(__file__))

### Configuration settings for the BroderClocks module ###

### Clock animation parameters ###
# time for single rotation of the clock
# time_rotate = 1.2 #1.35 #2.0**(0.5)
# period_li = [0,  # place holder
#              0.30, 0.33, 0.37, 0.41, 0.46,
#              0.51, 0.56, 0.63, 0.70, 0.77,
#              0.86, 0.96, 1.06, 1.18, 1.31,
#              1.46, 1.62, 1.80, 2.00, 2.22,
#              2.47, 2.74, 3.05]
# period_li = [i*1.5 for i in period_li]

period_li = np.arange(21)
period_li = 3*np.exp((-period_li)/12)

scale_min = 1
scale_max = len(period_li) - 1
default_rotate_ind = 6  # 19 # (22,) 19, 16, 13, 10, 7
# number of clock divisions that register as a unique place to click
num_divs_click = 80
# seconds / frame; display update rate to aim for
ideal_wait_s = 0.05
# auto save time in minutes
auto_save_time = 1
# starting point of the highest scorer
frac_period = 4.0 / 8.0  # 4.0/8.0 # 7, 6, 5, 4, 3, 2, 1
theta0 = frac_period * 2.0 * np.pi  # numpy.pi

# words per min tracking
wpm_history_length = 20


### Algorithm parameters ###
# winning score difference
win_diff_base = np.log(99)
win_diff_high = np.log(999)
max_init_diff = win_diff_base - np.log(4)
# learning press distribution or not
is_learning = True
is_pre_learning = True
# whether to output data
is_write_data = True
# last index to include when "undo"-ing scores
undo_index = 5
# time to delay learning to wait for "undos" (The value "0" means learn from the winner this round)
learn_delay = 2
# click density prior
## prior def
mu0 = 0.05  # on a range [-1s,1s]
sigma0 = 0.14  # on a range [-1s,1s]
sigma0_sq = sigma0 * sigma0
range0 = 2
