#!/usr/bin/python

######################################
#    Copyright 2009 Tamara Broderick
#    This file is part of Nomon Keyboard.
#
#    Nomon Keyboard is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Nomon Keyboard is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Nomon Keyboard.  If not, see <http://www.gnu.org/licenses/>.
######################################

import numpy as np
from PyQt5 import QtGui
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

print(period_li)
scale_min = 1
scale_max = len(period_li) - 1
default_rotate_ind = 10  # 19 # (22,) 19, 16, 13, 10, 7
# number of clock divisions that register as a unique place to click
num_divs_click = 80
# seconds / frame; display update rate to aim for
ideal_wait_s = 0.05
# auto save time in minutes
auto_save_time = 5
# starting point of the highest scorer
frac_period = 4.0 / 8.0  # 4.0/8.0 # 7, 6, 5, 4, 3, 2, 1
theta0 = frac_period * 2.0 * np.pi  # numpy.pi

# words per min tracking
wpm_history_length = 20



### Colors ###
# Background Color
bg_color_highlt = "#ddf6dd"

#  clock colors [regular, high_contrast]
clock_bg_color = [QtGui.QColor(255, 255, 255), QtGui.QColor(255, 255, 255)]

clock_text_color = [QtGui.QColor(0, 0, 0), QtGui.QColor(0, 0, 0)]
clock_text_hl_color = [QtGui.QColor(0, 0, 0), QtGui.QColor(200, 0, 0)]
clock_text_reg_color = [QtGui.QColor(0, 0, 0), QtGui.QColor(0, 0, 200)]
# default
default_hh_color = [QtGui.QColor(255, 0, 0), QtGui.QColor(0, 0, 0)]

default_selct_color = [QtGui.QColor(20, 245, 20), QtGui.QColor(20, 245, 20)]
default_highlt_color = [QtGui.QColor(0, 0, 255), QtGui.QColor(255, 0, 0)]
default_reg_color = [QtGui.QColor(0, 0, 0), QtGui.QColor(0, 0, 255)]

# bar
bar_hh_selct_color =[QtGui.QColor(10, 255, 10), QtGui.QColor(10, 255, 10)]
bar_hh_highlt_color = [QtGui.QColor(75, 75, 255), QtGui.QColor(255, 0, 0)]
bar_hh_reg_color = [QtGui.QColor(0, 0, 0), QtGui.QColor(00, 0, 255)]

bar_mh_selct_color = [QtGui.QColor(20, 245, 20), QtGui.QColor(20, 245, 20)]
bar_mh_highlt_color = [QtGui.QColor(150, 150, 255), QtGui.QColor(255, 150, 150)]
bar_mh_reg_color = [QtGui.QColor(170, 170, 170), QtGui.QColor(150, 150, 255)]

# ball
ball_mh_selct_color = [QtGui.QColor(20, 245, 20), QtGui.QColor(20, 245, 20)]
ball_mh_highlt_color = [QtGui.QColor(150, 150, 255), QtGui.QColor(255, 150, 150)]
ball_mh_reg_color = [QtGui.QColor(100, 100, 100), QtGui.QColor(150, 150, 255)]

# pac_man
pac_man_selct_color = [QtGui.QColor(20, 245, 20), QtGui.QColor(20, 245, 20)]
pac_man_highlt_color = [QtGui.QColor(0, 0, 255), QtGui.QColor(255, 0, 0)]
pac_man_reg_color = [QtGui.QColor(0, 0, 0), QtGui.QColor(0, 0, 255)]

### Fonts ###
base_font = 'helvetica'
splash_font = [QtGui.QFont(base_font, 11), QtGui.QFont(base_font, 15), QtGui.QFont(base_font, 22)]
welcome_main_font = [QtGui.QFont(base_font, 11), QtGui.QFont(base_font, 15), QtGui.QFont(base_font, 22)]
welcome_sub_font = [QtGui.QFont(base_font, 9), QtGui.QFont(base_font, 12), QtGui.QFont(base_font, 18)]
clock_font = QtGui.QFont(base_font)
clock_font.setBold(False)

top_bar_font = [QtGui.QFont(base_font, 11), QtGui.QFont(base_font, 15), QtGui.QFont(base_font, 24)]
for font in top_bar_font:
    font.setStretch(80)
    font.setBold(True)

text_box_font = [QtGui.QFont(base_font, 11), QtGui.QFont(base_font, 15), QtGui.QFont(base_font, 24)]
for font in text_box_font:
    font.setStretch(90)

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
