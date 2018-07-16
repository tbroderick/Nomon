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

import numpy
from PyQt4 import QtGui
import pickle

### Configuration settings for the BroderClocks module ###

### Clock animation parameters ###
# time for single rotation of the clock
# time_rotate = 1.2 #1.35 #2.0**(0.5)
period_li = [0,  # place holder
             0.30, 0.33, 0.37, 0.41, 0.46,
             0.51, 0.56, 0.63, 0.70, 0.77,
             0.86, 0.96, 1.06, 1.18, 1.31,
             1.46, 1.62, 1.80, 2.00, 2.22,
             2.47, 2.74, 3.05]
period_li = [i*1.5 for i in period_li]
start_speed = pickle.load(open("user_preferences/start_speed.p", 'rb'))
scale_min = 1
scale_max = len(period_li) - 1
default_rotate_ind = 19  # 19 # (22,) 19, 16, 13, 10, 7
# number of clock divisions that register as a unique place to click
num_divs_click = 80
# seconds / frame; display update rate to aim for
ideal_wait_s = 0.05
# starting point of the highest scorer
frac_period = 4.0 / 8.0  # 4.0/8.0 # 7, 6, 5, 4, 3, 2, 1
theta0 = frac_period * 2.0 * numpy.pi  # numpy.pi

# words per min tracking
wpm_history_length = 20


class Stack(list):

    def __init__(self, max_size):
        super(Stack, self).__init__()
        self.max_size = max_size

    def __add__(self, other):
        if len(self) < self.max_size:
            self.insert(0, other)
        else:
            self.pop(-1)
            self.insert(0, other)

    def average(self):
        return 60./(float(sum(self)) / float(len(self)))


### Colors ###
# Background Color
bg_color_highlt = "#ddf6dd"
high_contrast = pickle.load(open("user_preferences/high_contrast.p", 'rb'))
if high_contrast:

    # clock colors
    clock_bg_color = QtGui.QColor(255, 255, 255)

    clock_text_color = QtGui.QColor(0, 0, 0)
    clock_text_hl_color = QtGui.QColor(0, 0, 200)
    clock_text_reg_color = QtGui.QColor(200, 0, 0)
    # default
    default_hh_color = QtGui.QColor(0, 200, 0)

    default_selct_color = QtGui.QColor(20, 245, 20)
    default_reg_color = QtGui.QColor(255, 0, 0)
    default_highlt_color = QtGui.QColor(0, 0, 255)

    # bar
    bar_hh_selct_color = QtGui.QColor(10, 255, 10)
    bar_hh_reg_color = QtGui.QColor(255, 0, 0)
    bar_hh_highlt_color = QtGui.QColor(0, 0, 255)

    bar_mh_selct_color = QtGui.QColor(20, 245, 20)
    bar_mh_reg_color = QtGui.QColor(255, 150, 150)
    bar_mh_highlt_color = QtGui.QColor(150, 150, 255)

    # ball
    ball_mh_selct_color = QtGui.QColor(20, 245, 20)
    ball_mh_reg_color = QtGui.QColor(255, 150, 150)
    ball_mh_highlt_color = QtGui.QColor(150, 150, 255)

    # pac_man
    pac_man_selct_color = QtGui.QColor(20, 245, 20)
    pac_man_reg_color = QtGui.QColor(255, 0, 0)
    pac_man_highlt_color = QtGui.QColor(0, 0, 255)

else:
    # clock colors
    clock_bg_color = QtGui.QColor(255, 255, 255)
    clock_text_color = QtGui.QColor(0, 0, 0)
    # default
    default_hh_color = QtGui.QColor(255, 0, 0)

    default_selct_color = QtGui.QColor(20, 245, 20)
    default_highlt_color = QtGui.QColor(0, 0, 255)
    default_reg_color = QtGui.QColor(0, 0, 0)

    # bar
    bar_hh_selct_color = QtGui.QColor(10, 255, 10)
    bar_hh_highlt_color = QtGui.QColor(75, 75, 255)
    bar_hh_reg_color = QtGui.QColor(0, 0, 0)

    bar_mh_selct_color = QtGui.QColor(20, 245, 20)
    bar_mh_highlt_color = QtGui.QColor(150, 150, 255)
    bar_mh_reg_color = QtGui.QColor(170, 170, 170)

    # ball
    ball_mh_selct_color = QtGui.QColor(20, 245, 20)
    ball_mh_highlt_color = QtGui.QColor(150, 150, 255)
    ball_mh_reg_color = QtGui.QColor(100, 100, 100)

    # pac_man
    pac_man_selct_color = QtGui.QColor(20, 245, 20)
    pac_man_highlt_color = QtGui.QColor(0, 0, 255)
    pac_man_reg_color = QtGui.QColor(0, 0, 0)

### Fonts ###
base_font = 'consolas'
font_scale = pickle.load(open("user_preferences/font_scale.p", 'rb'))

if font_scale == 'med':
    font_scale = 1
elif font_scale == 'large':
    font_scale = 1.5
elif font_scale == 'small':
    font_scale = 0.75
splash_font = QtGui.QFont(base_font, 15*font_scale)

welcome_main_font = QtGui.QFont('Consolas', 15*font_scale)
welcome_sub_font = QtGui.QFont('Consolas', 12*font_scale)
clock_font = QtGui.QFont(base_font)
clock_font.setBold(False)

top_bar_font = QtGui.QFont(base_font, 16*font_scale)
top_bar_font.setStretch(80)
top_bar_font.setBold(True)

text_box_font = QtGui.QFont(base_font, 20*font_scale)
text_box_font.setStretch(90)



### Algorithm parameters ###
# winning score difference
win_diff_base = numpy.log(99)
win_diff_high = numpy.log(999)
max_init_diff = win_diff_base - numpy.log(4)
# learning press distribution or not
is_learning = True
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
