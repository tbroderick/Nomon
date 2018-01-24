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

import config

### Configuration settings for the Keyboard module ###

### Keyboard setup ###
# characters in the keys
space_char = '_'
mybad_char = 'Undo'
#yourbad_char = 'Yours'
yourbad_char = 'Undo+'
break_char = '.'
back_char = 'Delete'
# word length to display in completions
max_chars_display = 11
## alphabetic
# always put alpha-numeric keys first (self.N_alpha_keys)
key_chars = [	['a','b','c','d','e'],
		['f','g','h','i','j'],
		['k','l','m','n','o'],
		['p','q','r','s','t'],
		['u','v','w','x','y'],
		['z',space_char,break_char,back_char,mybad_char]
		]
## qwerty
#key_chars = [	['q','w','e','r','t','y','u','i','o','p'],
#		['a','s','d','f','g','h','j','k','l','\''],
#		['z','x','c','v','b','n','m',',','.','?'],
#		[space_char, undo_char]
#		]

### Events ###
# event selection
joy_evt = "<<JoyFoo>>"
key_evt = "<space>"
# event to use as switch
target_evt = key_evt

### Speech ###
#talk_winner_on = False

### Word display parameters ###
## sizes
# base window size (for relative size calculations)
base_window_width = 1200
base_window_height = 700
# clock radius
base_clock_rad = 10
clock_rad = 10
# word width
base_word_w = 160
word_w = 160
# words per key
N_pred = 3
## colors
# color of key text
key_text_color = "black"
# color of key and outline
key_color = "" #white
key_outline_color = config.circle_outline_color
# color of typed text
type_color = "black"
# color of text to be undone
undo_type_color = "#%02x%02x%02x" % (0,200,0)
## fonts
# font of key text
base_key_pt = 28
key_pt = 28
key_font = ("Helvetica",key_pt,"bold")
# font of word text
base_word_pt = 12
word_pt = 12
word_font = ("Helvetica",word_pt)
# font of typed text
base_type_pt = 16
type_pt = 16
type_font = ("Helvetica",type_pt)
# histogram color
plot_color = "blue"
plot_outline_color = "black"
# color of key back when win
key_win_color = "#%02x%02x%02x" % (10, 220, 10)
fill_win_color = "#%02x%02x%02x" % (189,252,201)
# time to leave winner info up (milliseconds)
winner_time = 2000

### Data collection ###
# data file prefix
file_pre = "data/clocks."
# data file suffix
file_suff = ".txt"
# train file name
#TESTING:train_file_name = "../corpus/ANC-token-proc-small.txt"
train_file_name = "corpus/BNC-token-proc.txt" #removed "../" from beginning
# phrases file
base_file = "phrases/base_file_phrases.txt"
phrase_pre = "phrases/phrase_rand"
phrase_suff = ".txt"
## saving settings
# where to save
dump_pre = "save/settings."
dump_suff = ".dump"
# max time for a round
max_round_sec = 14*60
# whether or not to have pause (and how long: milliseconds)
pause_set = True
pause_length = 400

### Language model ###
# probability threshold for inclusion of word in the display
prob_thres = 0.001
# undo prior prob
undo_prob = 1.0/40
# break prior prob
break_prob = 1.0/20
# back prior prob
back_prob = 1.0/40
# remaining, non-special probability
rem_prob = 1.0 - undo_prob - break_prob - back_prob