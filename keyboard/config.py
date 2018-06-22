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

### Colors ###
# background
bgcolor = "white"  # "#%02x%02x%02x" % (0,0,150)
# clockface color
circle_low_color = "#%02x%02x%02x" % (255, 255, 255)
circle_high_color = "#FFFF69"  # "yellow"
circle_off_color = ""
circle_outline_color = "black"
circle_win_color = circle_outline_color  # "#%02x%02x%02x" % (0,200,0)
circle_lose_color = circle_outline_color  # "red"
# outline sizes
circle_outline_width = 1.0
circle_lose_width = circle_outline_width  # 3
circle_win_width = circle_outline_width  # 3
# noon position (desired hitting point) color
noon_color = "#%02x%02x%02x" % (255, 0, 0)
# color of the moving hour hand
hour_color = "#%02x%02x%02x" % (0, 0, 0)
# hand sizes
hand_width = 1.5
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
