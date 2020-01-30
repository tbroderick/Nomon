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


import config
import pickle

### Configuration settings for the SimulatedUser module ###

### SimulatedUser setup ###
# characters in the keys
space_char = ' '
mybad_char = '@'
# yourbad_char = 'Yours'
yourbad_char = 'Undo+'
break_chars = ['.', ',', '?', '!']
back_char = '#'
clear_char = '$'

# word length to display in completions
max_chars_display = 11
num_words_total = 17
## alphabetic
# always put alpha-numeric keys first (self.N_alpha_keys)

key_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                   'u', 'v', 'w', 'x', 'y', 'z', '\'', space_char, '\'', break_chars[0], break_chars[1],
                   break_chars[2], break_chars[3], back_char, clear_char, mybad_char]
alpha_target_layout = [['a', 'b', 'c', 'd', 'e'],
                 ['f', 'g', 'h', 'i', 'j'],
                 ['k', 'l', 'm', 'n', 'o'],
                 ['p', 'q', 'r', 's', 't'],
                 ['u', 'v', 'w', 'x', 'y'],
                 ['z', 'BREAKUNIT', "SPACEUNIT", 'BACKUNIT', 'UNDOUNIT']]

## qwerty
qwerty_target_layout = [['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
                    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', break_chars[3]],
                    ['z', 'x', 'c', 'v', 'b', 'n', 'm', break_chars[0], break_chars[1], break_chars[2]],
                    [ back_char, space_char, clear_char, 'UNDOUNIT']]

pretrain_target_layout = [  [0,  1,  2,  3,  4],
                            [5,  6,  7,  8,  9],
                            [10, 11, 12, 13, 14],
                            [15, 16, 17, 18, 19]]

# get gaussian distribution
bars = [4.1731209137640166e-11, 1.5674042704727563e-10, 5.702330790217924e-10, 2.009440319647259e-09,
        6.858815826469396e-09, 2.2676420114286876e-08, 7.261915168381362e-08, 2.2525745454100865e-07,
        6.767971122297686e-07, 1.969650386894775e-06, 5.552276918629734e-06, 1.5160181992883207e-05,
        4.009489083361327e-05, 0.00010271289727370694, 0.0002548662025258791, 0.0006125631118014535,
        0.001426069713163289, 0.0032157479134091965, 0.007023839199846974, 0.01485998764716699, 0.03045184848219981,
        0.0604449741201335, 0.11621389459417346, 0.21642490682430432, 0.3903981461621635, 0.6821181069890906,
        1.1544170528966142, 1.8924186208565767, 3.0048515131831763, 4.621470051256386, 6.884756647011963,
        9.934553867306171, 13.88543429703574, 18.798443462933843, 24.65106218552027, 31.31127178097519,
        38.52273404437159, 45.90762451643071, 52.99121328326851, 59.2480729571828, 64.16466330246335, 67.30834836361127,
        68.39010521167417, 67.30834836361129, 64.16466330246332, 59.2480729571828, 52.99121328326855, 45.90762451643069,
        38.52273404437159, 31.311271780975158, 24.65106218552027, 18.79844346293387, 13.885434297035717,
        9.934553867306171, 6.884756647011954, 4.621470051256386, 3.0048515131831834, 1.8924186208565716,
        1.1544170528966142, 0.6821181069890888, 0.3903981461621635, 0.21642490682430507, 0.11621389459417325,
        0.06044497412013371, 0.03045184848219981, 0.014859987647167044, 0.007023839199847036, 0.0032157479134091965,
        0.0014260697131632965, 0.0006125631118014535, 0.00025486620252588053, 0.00010271289727370786,
        4.009489083361327e-05, 1.5160181992883289e-05, 5.552276918629734e-06, 1.969650386894789e-06,
        6.767971122297759e-07, 2.2525745454100865e-07, 7.261915168381387e-08, 2.2676420114286876e-08]

### Events ###
# event selection
joy_evt = "<<JoyFoo>>"
key_evt = "<space>"
# event to use as switch
target_evt = key_evt

### Speech ###
# talk_winner_on = False

### Word display parameters ###
## sizes
# base window size (for relative size calculations)
base_window_width = 1200
base_window_height = 700
# clock radius
base_clock_rad = 10  # 10

pre_clock_rad = 200
clock_rad = 10  # 10
# word width
base_word_w = 160
word_w = 160
# words per key
N_pred = 3
## colors
# color of key text
key_text_color = "black"
# color of key and outline
key_color = ""  # white
# color of typed text
type_color = "black"
# color of text to be undone
undo_type_color = "#%02x%02x%02x" % (0, 200, 0)
## fonts
# font of key text
base_key_pt = 28
key_pt = 28
key_font = ("Helvetica", key_pt, "bold")
# font of word text
base_word_pt = 12
word_pt = 12
word_font = ("Helvetica", word_pt)
# font of typed text
base_type_pt = 16
type_pt = 16
type_font = ("Helvetica", type_pt)
# histogram color
plot_color = "blue"
plot_outline_color = "black"
# color of key back when win
key_win_color = "#%02x%02x%02x" % (10, 220, 10)
fill_win_color = "#%02x%02x%02x" % (189, 252, 201)
# time to leave winner loading_text up (milliseconds)
winner_time = 2000

### Data collection ###
# data file prefix
file_pre = "data/clocks."
# data file suffix
#file_suff = ".txt"
file_stuff = ".pickle"
# train file name
# TESTING:train_file_name = "../corpus/ANC-token-proc-small.txt"
# train_file_name_default = "corpus/merged_ce-0.2.txt"  # removed "../" from beginning
# train_file_name_censored = "corpus/merged_ce-0.2_censored.txt"

# phrases file
base_file = "phrases/base_file_phrases.txt"
phrase_pre = "phrases/phrase_rand"
phrase_suff = ".txt"

## saving settings
# where to save
dump_pre = "save/settings."
#dump_suff = ".dump"
dump_stuff = ".pickle"
# max time for a round
max_round_sec = 14 * 60
# whether or not to have pause (and how long: milliseconds)
pause_set = True
pause_length = 1000

### Language model ###
# probability threshold for inclusion of word in the display
prob_thres = 0.008
# undo prior prob
undo_prob = 1.0 / 40
# back prior prob
back_prob = 1.0 / 40
# remaining, non-special probability
rem_prob = 1.0 - undo_prob - back_prob
