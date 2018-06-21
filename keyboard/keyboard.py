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
#    Nomon Keyboard is distributed in the hope that it will be useful,dfg
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Nomon Keyboard.  If not, see <http://www.gnu.org/licenses/>.
######################################

import broderclocks
import dtree
import config
# import glob
import kconfig
import string
import time
import numpy

from keyboard_GUI_PyQt import *

if kconfig.target_evt == kconfig.joy_evt:
    import pygame
import sys
import cPickle
import random
import os


class Keyboard(GUI):
    def __init__(self, layout, screen_res):
        super(Keyboard, self).__init__(layout, screen_res)

        # check that number of arguments is valid
        if len(sys.argv) < 3:  # replaced with a default 0 0
            # print "Error: Too few (" + str(len(sys.argv)-1) + " < 2) arguments"
            # print "Usage: python keyboard.py user-id use-number proposed-window-width proposed-window-height"
            # sys.exit() #replaced quit() with this
            # quit()
            user_id = 0
            use_num = 0
        # read arguments
        else:
            user_id = string.atoi(sys.argv[1])
            use_num = string.atoi(sys.argv[2])
        self.user_id = user_id
        self.use_num = use_num
        # read extra arguments if they're there
        if len(sys.argv) > 3:
            prop_width = string.atoi(sys.argv[4])
        else:
            prop_width = kconfig.base_window_width
        if len(sys.argv) > 4:
            prop_height = string.atoi(sys.argv[3])
        else:
            prop_height = kconfig.base_window_height
        self.set_sizes(prop_height, prop_width)

        ### initialize ###
        ## initialize pygame and joystick
        if kconfig.target_evt is kconfig.joy_evt:
            pygame.init()
            if pygame.joystick.get_count() < 1:
                # no joysticks found
                print "Please connect a joystick.\n"
                self.quit(None)
            else:
                # create a new joystick object from
                # ---the first joystick in the list of joysticks
                Joy0 = pygame.joystick.Joystick(0)
                # tell pygame to record joystick events
                Joy0.init()
            ## start looking for events
            self.parent.after(0, self.find_events)
        ## not in selection pause
        self.in_pause = False

        ## determine keyboard positions
        self.init_locs()
        ## get old data if there is such
        if self.use_num > 0:
            # input file (if such exists) for histogram
            dump_file_in = kconfig.dump_pre + "clocks." + str(self.user_id) + "." + str(
                self.use_num - 1) + kconfig.dump_suff
            fid = open(dump_file_in, 'r')
            in_data = cPickle.load(fid)
            fid.close()

            # period
            self.rotate_index = in_data[0]
            prev_data = in_data[1]
        else:
            self.rotate_index = config.default_rotate_ind
            prev_data = []
        ## set up file handle for printing useful stuff
        self.undefined = False
        if config.is_write_data:
            self.gen_handle()
            self.num_presses = 0
            self.file_handle.write(
                "params " + str(config.period_li[config.default_rotate_ind]) + " " + str(config.theta0) + "\n")
            self.file_handle.write("start " + str(time.time()) + "\n")
        else:
            self.file_handle = None
        ## set up canvas for displaying stuff
        # self.gen_canvas()
        self.gen_scale()
        # self.gen_button_frame()
        # self.toggle_pause_button()
        self.pause_set = False
        # self.gen_learn_button()
        # self.toggle_pause_button()
        ## set up "typed" text
        self.typed = ""
        self.btyped = ""
        self.context = ""
        self.old_context_li = [""]
        self.last_add_li = [0]
        ## set up "talked" text
        self.talk_file = "talk.txt"
        ## set up dictionary tree
        train_handle = open(kconfig.train_file_name, 'r')
        self.dt = dtree.DTree(train_handle)
        train_handle.close()
        # check for speech
        talk_fid = open(self.talk_file, 'w')
        ##	talk_fid.write(".. Festival is ready ?")
        ##	talk_fid.close()
        ##	out = os.system("/usr/bin/festival --tts talk.txt")
        ##	if out == 32512:
        ##		self.has_festival = False
        ##	else:
        ##		self.has_festival = True
        # write keys
        # self.init_keys()
        # write words
        self.init_words()
        # write typed text
        self.init_typed()

        self.bc_init = False
        self.initUI()

        ## set up broderclocks
        self.bc = broderclocks.BroderClocks(self, self.clock_centers, self.win_diffs, kconfig.clock_rad,
                                            self.file_handle, self.words_on, self.words_off, kconfig.key_color,
                                            time.time(), use_num, user_id, self.time_rotate, prev_data)
        self.wait_s = self.bc.get_wait()
        # get language model results
        self.gen_word_prior(False)
        self.bc.init_follow_up(self.word_score_prior)
        # write key text
        self.init_key_text()
        # draw histogram
        self.init_histogram()
        # bring word text to the front
        self.raise_words()

        ### animate ###
        self.on_timer()

        # which ones to try predicting on
        try_pred = []
        for row in range(0, self.N_rows):
            for col in range(0, self.N_keys_row[row]):
                try_pred = kconfig.key_chars[row][col].isalpha()


    def find_events(self):
        ## check everything in the queue of pygame events
        events = pygame.event.get()
        for event in events:
            # event type for pressing any of the joystick buttons down
            if event.type == pygame.JOYBUTTONDOWN:
                # generate the event I've defined
                self.canvas.event_generate(kconfig.joy_evt)

        ## return to check for more events in a moment
        self.parent.after(20, self.find_events)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Space:
            self.on_press()

    def init_locs(self):
        # size of keyboard
        self.N_rows = len(kconfig.key_chars)
        self.N_keys_row = []
        self.N_keys = 0
        self.N_alpha_keys = 0
        for row in range(0, self.N_rows):
            n_keys = len(kconfig.key_chars[row])
            for col in range(0, n_keys):
                if kconfig.key_chars[row][col].isalpha() and (len(kconfig.key_chars[row][col]) == 1):
                    self.N_alpha_keys = self.N_alpha_keys + 1
            self.N_keys_row.append(n_keys)
            self.N_keys += n_keys

        # width difference when include letter
        word_clock_offset = 7 * kconfig.clock_rad
        rect_offset = word_clock_offset - kconfig.clock_rad
        word_offset = 8.5 * kconfig.clock_rad
        rect_end = rect_offset + kconfig.word_w

        # clock, key, word locations
        self.clock_centers = []
        self.win_diffs = []
        self.word_locs = []
        self.char_locs = []
        self.rect_locs = []
        self.keys_li = []
        self.keys_ref = []
        index = 0  # how far into the clock_centers matrix
        word = 0  # word index
        key = 0  # key index
        # kconfig.N_pred = 3 # number of words per key
        self.key_height = 6.5 * kconfig.clock_rad
        self.w_canvas = 0
        self.index_to_wk = []  # overall index to word or key index
        for row in range(0, self.N_rows):
            y = row * self.key_height
            self.w_canvas = max(self.w_canvas, self.N_keys_row[row] * (6 * kconfig.clock_rad + kconfig.word_w))
            for col in range(0, self.N_keys_row[row]):
                x = col * (6 * kconfig.clock_rad + kconfig.word_w)
                ## predictive words
                self.clock_centers.append([x + word_clock_offset, y + 1 * kconfig.clock_rad])
                self.clock_centers.append([x + word_clock_offset, y + 3 * kconfig.clock_rad])
                self.clock_centers.append([x + word_clock_offset, y + 5 * kconfig.clock_rad])
                # win diffs
                self.win_diffs.extend([config.win_diff_base, config.win_diff_base, config.win_diff_base])
                # word position
                self.word_locs.append([x + word_offset, y + 1 * kconfig.clock_rad])
                self.word_locs.append([x + word_offset, y + 3 * kconfig.clock_rad])
                self.word_locs.append([x + word_offset, y + 5 * kconfig.clock_rad])
                # rectangles
                self.rect_locs.append([x + rect_offset, y	 ,x +rect_end , y + 2* kconfig.clock_rad])
                self.rect_locs.append(
                    [x + rect_offset, y + 2 * kconfig.clock_rad, x + rect_end, y + 4 * kconfig.clock_rad])
                self.rect_locs.append(
                    [x + rect_offset, y + 4 * kconfig.clock_rad, x + rect_end, y + 6 * kconfig.clock_rad])
                # indices
                self.index_to_wk.append(word)
                self.index_to_wk.append(word + 1)
                self.index_to_wk.append(word + 2)
                index += 3
                word += 3

                ## key character
                # reference to index of key character
                key_char = kconfig.key_chars[row][col]
                self.keys_li.append(kconfig.key_chars[row][col])
                self.keys_ref.append(index)
                self.index_to_wk.append(key)
                # key character position
                self.char_locs.append([x + 2 * kconfig.clock_rad, y + 3 * kconfig.clock_rad])
                # clock position for key character
                self.clock_centers.append([x + 1 * kconfig.clock_rad, y + 3 * kconfig.clock_rad])
                # rectangles
                self.rect_locs.append([x, y, x + rect_offset, y + 6 * kconfig.clock_rad])
                # win diffs
                if (key_char == kconfig.mybad_char) or (key_char == kconfig.yourbad_char) or (
                        key_char == kconfig.back_char):  # or (key_char == kconfig.break_char)
                    self.win_diffs.append(config.win_diff_high)
                else:
                    self.win_diffs.append(config.win_diff_base)
                index += 1
                key += 1
        # space for the keyboard
        self.h_canvas = self.N_rows * (6.5 * kconfig.clock_rad)
        # space for the typed text and histogram
        self.typed_loc = [0, self.h_canvas]  # anchor is nw, so no " + kconfig.clock_rad"

        # buffer for side text
        self.w_canvas += 2 * kconfig.clock_rad

        # height for bottom two
        self.height_bot = 3 * self.key_height

    def gen_handle(self):
        # file handle
        data_file = kconfig.file_pre + str(self.user_id) + "." + str(self.use_num) + kconfig.file_suff
        self.file_handle = open(data_file, 'w')

    def gen_canvas(self):
        # self.canvas = Tkinter.Canvas(self.parent, width=self.w_canvas, height=self.h_canvas, background=config.bgcolor)
        # self.parent.columnconfigure(0, minsize=self.w_canvas / 2.0)
        # self.parent.columnconfigure(1, minsize=self.w_canvas / 2.0)
        # self.parent.rowconfigure(0, minsize=self.key_height)
        # self.parent.rowconfigure(1, minsize=self.h_canvas)
        # self.parent.rowconfigure(2, minsize=self.height_bot)
        # self.canvas.grid(row=1, column=0, columnspan=2)
        self.parent.bind(kconfig.target_evt, self.on_press)
        # self.canvas.focus_set()  # so don't have to click on the canvas beforehand

        # tool tip
        # self.keyboard_tooltip = ToolTip(self.canvas, follow_mouse=1, font=kconfig.word_font,
        #                                 text="This is the Nomon Keyboard. To select an option, find the clock immediately to its left. Press the spacebar when the moving hand is near noon.")

    def gen_scale(self):
        scale_length = self.w_canvas / 2  # (len(kconfig.key_chars[0])-1)*kconfig.word_w
        tick_int = int((len(config.period_li) - 1) * kconfig.word_pt * 3 / (1.0 * scale_length)) + 1

        # frame
        # self.scale_frame = Tkinter.Frame(self.parent, width=scale_length, height=self.key_height)
        #         # self.scale_frame.grid(row=0, column=0)
        #         # # scale
        #         # self.scale = Tkinter.Scale(self.scale_frame, orient=Tkinter.HORIZONTAL, label="Clock Rotation Speed",
        #         #                            length=scale_length, from_=config.scale_min, to=config.scale_max,
        #         #                            tickinterval=tick_int, command=self.change_speed, font=kconfig.word_font)
        #         # # careful; scale is for speed, but the settings are saved as clock periods
        #         # self.speed_index = config.scale_max - self.rotate_index + 1
        #         # self.scale.set(self.speed_index)
        #         # self.scale.pack(side=Tkinter.TOP)
        # ******
        self.time_rotate = config.period_li[self.rotate_index]

        # tool tip
        # self.scale_tooltip = ToolTip(self.scale, follow_mouse=1, font=kconfig.word_font,
        #                              text="This slider scales the speed of clock rotation. Higher values correspond to the clock hand moving faster.")
        #
        # # bind right and left arrow events
        # self.canvas.bind("<Left>", self.dec_speed)
        # self.canvas.bind("<Right>", self.inc_speed)

    def toggle_pause_button(self, value):
        self.pause_set = value
        self.sldLabel.setFocus()

    def toggle_talk_button(self, value):
        self.talk_set = value
        self.sldLabel.setFocus()  # focus on not toggle-able widget to allow keypress event

    def toggle_learn_button(self, value):
        config.is_learning = value
        self.sldLabel.setFocus()  # focus on not toggle-able widget to allow keypress event

    def change_speed(self, index):
        # speed (as shown on scale)
        speed_index = int(index)
        # period (as stored in config.py)
        self.rotate_index = config.scale_max - speed_index + 1
        old_rotate = self.time_rotate
        self.time_rotate = config.period_li[self.rotate_index]
        self.bc.change_period(self.time_rotate)
        self.wait_s = self.bc.get_wait()

        # note period change in log file
        self.file_handle.write("speed " + str(time.time()) + " " + str(old_rotate) + " " + str(self.time_rotate) + "\n")

        # update the histogram
        self.draw_histogram()

    def set_sizes(self, prop_height, prop_width):
        ratioH = prop_height / (1.0 * kconfig.base_window_height)
        ratioW = prop_width / (1.0 * kconfig.base_window_width)
        # choose the most stringent bound
        ratio = min(ratioH, ratioW)

        # change params
        kconfig.word_w = int(ratio * kconfig.base_word_w)
        kconfig.clock_rad = int(ratio * kconfig.base_clock_rad)
        kconfig.key_pt = int(ratio * kconfig.base_key_pt)
        kconfig.word_pt = int(ratio * kconfig.base_word_pt)
        kconfig.type_pt = int(ratio * kconfig.base_type_pt)
        # propagate
        kconfig.key_font = ("Helvetica", kconfig.key_pt, "bold")
        kconfig.word_font = ("Helvetica", kconfig.word_pt)
        kconfig.type_font = ("Helvetica", kconfig.type_pt)

    def inc_speed(self, evt):
        index = self.scale.get()
        self.scale.set(min(config.scale_max, index + 1))

    def dec_speed(self, evt):
        index = self.scale.get()
        self.scale.set(max(config.scale_min, index - 1))

    def init_keys(self):
        for key in range(0, self.N_keys):
            self.canvas.create_rectangle(
                [self.char_locs[key][0] - 2 * kconfig.clock_rad, self.char_locs[key][1] - 3 * kconfig.clock_rad,
                 self.char_locs[key][0] + 4 * kconfig.clock_rad + kconfig.word_w,
                 self.char_locs[key][1] + 3 * kconfig.clock_rad], fill=kconfig.key_color,
                outline=kconfig.key_outline_color)

        # sub-keys for coloring on wins
        self.subkey_id = []
        for rect_loc in self.rect_locs:
            self.subkey_id.append(self.canvas.create_rectangle(rect_loc, fill=kconfig.key_color, outline=""))

    def init_key_text(self):
        self.key_id = []
        for key in range(0, self.N_keys):
            pass
            # self.key_id.append(
            #     self.canvas.create_text(self.char_locs[key], text=self.keys_li[key], fill=kconfig.key_text_color,
            #                             font=kconfig.key_font, anchor='w'))

    def init_histogram(self):
        ### histogram
        bars = self.bc.get_histogram()
        self.bars = bars

        ### undo_text
        self.undo_loc = [
            (self.N_keys_row[self.N_rows - 1] - 1) * (6 * kconfig.clock_rad + kconfig.word_w) - self.w_canvas / 2,
            2 * kconfig.clock_rad]
        # undo text next to undo button
        # self.undo_id = self.histo_canvas.create_text(self.undo_loc,
        #                                              text='', fill=kconfig.undo_type_color, font=kconfig.key_font,
        #                                              width=self.w_canvas / 2, anchor='w')

        # tooltip to explain what the histogram is
        # self.histogram_tooltip = ToolTip(self.histo_canvas, follow_mouse=1, font=kconfig.word_font,
        #                                  text="This is Nomon's estimate of where you click relative to noon on the clocks. The thinner the distribution, the more precisely Nomon thinks you are clicking.")

    def draw_histogram(self, bars=None):
        if bars == None:
            bars = self.bc.get_histogram()
        # bars = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.bars = bars
        self.histogram.repaint()

    def init_words(self):
        (self.words_li, self.word_freq_li, self.key_freq_li, self.top_freq, self.tot_freq, self.prefix) = self.dt.get_words(
            self.context, self.keys_li)
        self.word_id = []
        self.word_pair = []
        word = 0
        index = 0
        self.words_on = []
        self.words_off = []
        len_con = len(self.context)
        for key in range(0, self.N_alpha_keys):
            for pred in range(0, kconfig.N_pred):
                word_str = self.words_li[key][pred]
                len_word = len(word_str)
                if (len_con > 1) and (len_word > kconfig.max_chars_display):
                    word_str = "+" + word_str[len_con:len_word]
                self.word_pair.append((key, pred))
                # self.word_id.append(
                #     self.canvas.create_text(self.word_locs[word], text=word_str, fill=kconfig.key_text_color,
                #                             font=kconfig.word_font, anchor='w'))
                if word_str == '':
                    self.words_off.append(index)
                else:
                    self.words_on.append(index)
                word += 1
                index += 1
            self.words_on.append(index)
            self.word_pair.append((key,))
            index += 1
        for key in range(self.N_alpha_keys, self.N_keys):
            for pred in range(0, kconfig.N_pred):
                word_str = self.words_li[key][pred]
                self.word_pair.append((key, pred))
                # self.word_id.append(self.canvas.create_text(self.word_locs[word], text='', fill=kconfig.key_text_color,
                #                                             font=kconfig.word_font, anchor='w'))
                self.words_off.append(index)
                index += 1
            self.words_on.append(index)
            self.word_pair.append((key,))
            index += 1
        # Send words to GUI
        words = []
        for letter_group in self.words_li:
            for word in letter_group:
                if word != '':
                    words += [word]
        self.word_list = words

    def raise_words(self):
        pass
        for wid in self.word_id:

            self.canvas.tag_raise(wid)

    def draw_words(self):
        (self.words_li, self.word_freq_li, self.key_freq_li, self.top_freq, self.tot_freq, self.prefix) = self.dt.get_words(
            self.context, self.keys_li)

        word = 0
        index = 0
        self.words_on = []
        self.words_off = []
        len_con = len(self.context)
        for key in range(0, self.N_alpha_keys):
            key_char = self.keys_li[key]
            for pred in range(0, kconfig.N_pred):
                word_str = self.words_li[key][pred]
                len_word = len(word_str)
                if len_con > 1 and len_word > kconfig.max_chars_display:
                    word_str = "+" + word_str[len_con:len_word]
                # self.canvas.itemconfigure(self.word_id[word], text=word_str)
                if word_str == '':
                    self.words_off.append(index)
                else:
                    self.words_on.append(index)
                word += 1
                index += 1
            self.words_on.append(index)
            self.word_pair.append((key,))
            index += 1
        for key in range(self.N_alpha_keys, self.N_keys):
            for pred in range(0, kconfig.N_pred):
                word_str = self.words_li[key][pred]
                self.word_pair.append((key, pred))
                # self.word_id.append(self.canvas.create_text(self.word_locs[word], text='', fill=kconfig.key_text_color,
                #                                             font=kconfig.word_font, anchor='w'))
                self.words_off.append(index)
                index += 1
            self.words_on.append(index)
            self.word_pair.append((key,))
            index += 1
        print(self.words_li)
        # Send words to GUI
        words = []
        for letter_group in self.words_li:
            for word in letter_group:
                if word != '':
                    words += [word]

        self.word_list = words
        self.remove_clocks()

    def gen_word_prior(self, is_undo):
        self.word_score_prior = []
        N_on = len(self.words_on)
        if not is_undo:
            for index in self.words_on:
                pair = self.word_pair[index]
                # word case
                if len(pair) == 2:
                    (key, pred) = pair
                    prob = (self.word_freq_li[key][pred] + 1) * 1.0 / (self.tot_freq + N_on)
                    prob = prob * kconfig.rem_prob
                    self.word_score_prior.append(numpy.log(prob))
                else:
                    key = pair[0]
                    prob = (self.key_freq_li[key] + 1) * 1.0 / (self.tot_freq + N_on)
                    prob = prob * kconfig.rem_prob
                    if self.keys_li[key] == kconfig.mybad_char or self.keys_li[key] == kconfig.yourbad_char:
                        prob = kconfig.undo_prob
                    if self.keys_li[key] == kconfig.break_char:
                        prob = kconfig.break_prob
                    if self.keys_li[key] == kconfig.back_char:
                        prob = kconfig.back_prob
                    self.word_score_prior.append(numpy.log(prob))
        else:
            for index in self.words_on:
                pair = self.word_pair[index]
                if len(pair) == 1:
                    key = pair[0]
                    if (self.keys_li[key] == kconfig.mybad_char) or (self.keys_li[key] == kconfig.yourbad_char):
                        prob = kconfig.undo_prob
                        self.word_score_prior.append(numpy.log(prob))
                    else:
                        self.word_score_prior.append(0)
                else:
                    self.word_score_prior.append(0)

    def init_typed(self):
        return
        ## text box
        # frame
        self.type_frame = Tkinter.Frame(self.parent, width=self.w_canvas, height=self.height_bot)
        self.type_frame.grid(row=2, column=0)
        # scrollbar
        scrollbar = Tkinter.Scrollbar(self.type_frame)
        scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        # text
        self.typed_text = Tkinter.Text(self.type_frame, width=self.w_canvas / (2 * kconfig.type_pt),
                                       height=self.height_bot / (2 * kconfig.type_pt), font=kconfig.type_font,
                                       fg=kconfig.type_color, bg=config.bgcolor, wrap=Tkinter.CHAR, takefocus=0,
                                       yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.typed_text.yview)
        self.typed_text.pack()
        self.typed_text.insert(Tkinter.END, self.typed + "|")
        self.typed_text.tag_add("TYPED_UNDO", "1.0", "1.1")
        self.typed_text.tag_config("TYPED_UNDO", foreground=kconfig.undo_type_color)

    def draw_typed(self):
        # self.typed_text.delete("1.0", Tkinter.END)
        #         # self.typed_text.tag_delete("TYPED_UNDO");
        if len(self.last_add_li) > 1:
            last_add = self.last_add_li[-1]
            if last_add > 0:  # typed something
                new_text = self.typed[-last_add:len(self.typed)]
                undo_text = new_text
            elif last_add == -1:  # backspace
                new_text = ''
                print('Delete')
                last_add = 0
                undo_text = kconfig.back_char
        else:
            new_text = ''
            undo_text = new_text
            last_add = 0
        print("DRAW TEXT: ", new_text)
        previous_text = self.text_box.toPlainText()
        self.text_box.setText("<span style='color:#000000;'>"+previous_text+"</span><span style='color:#00dd00;'>"+new_text+"</span>")
        # self.typed_text.insert(Tkinter.END, self.typed[0:(len(self.typed) - last_add)])
        # self.typed_text.tag_add("TYPED_UNDO", Tkinter.END, Tkinter.END)
        # self.typed_text.insert(Tkinter.END, new_text, ("TYPED_UNDO"))
        # self.typed_text.insert(Tkinter.END, "|", ("TYPED_UNDO"))
        # self.typed_text.tag_config("TYPED_UNDO", foreground=kconfig.undo_type_color)
        # self.histo_canvas.itemconfigure(self.undo_id, text=undo_text)
        # self.typed_text.see(Tkinter.END)

    def on_timer(self):
        if self.bc_init:
            if not self.in_pause:
                start_t = time.time()
                self.bc.increment(start_t)

                # self.canvas.focus_set()  # so don't have to click on the canvas (e.g. if tooltip takes focus)

                # self.last_anim_call = self.canvas.after(max(0, int((self.wait_s - (time.time() - start_t)) * 1000)),
                #                                         self.on_timer)

    def on_press(self):
        # self.canvas.focus_set()

        if not self.in_pause:
            print("press")
            if config.is_write_data:
                self.num_presses += 1
                self.file_handle.write("press " + str(time.time()) + " " + str(self.num_presses) + "\n")
            self.bc.select(time.time())

    def highlight_winner(self, index):
        print("HIGHLIGHT WINNER", self.clock_index_to_text(index))
        if self.clocks[index] != '':
            self.clocks[index].selected = True
            self.clocks[index].repaint()
            time.sleep(2)

        # self.canvas.itemconfigure(self.subkey_id[index], fill=kconfig.key_win_color)
        # self.canvas.update_idletasks()
        #
        # self.canvas.after(kconfig.winner_time, self.end_winner, index)

    def clock_index_to_text(self, index):
        letter_num = int(index/4)
        letter_rem = index-letter_num*4
        if index < 26*4:
            if letter_rem < 3:
                return self.words_li[letter_num][letter_rem]
            return string.lowercase[letter_num]


    def end_winner(self, index):
        self.canvas.itemconfigure(self.subkey_id[index], fill=kconfig.key_color)

    def talk_winner(self, talk_string):
        pass

    ##	if self.has_festival:
    ##		if(talk_string == 'a'):
    ##			talk_string = 'ay'
    ##		elif(talk_string == 'the'):
    ##			talk_string = 'thee'
    ##		elif(talk_string == 'of'):
    ##			talk_string = 'of'
    ##		elif(talk_string == 'on'):
    ##			talk_string = 'on'
    ##		elif(talk_string == 'or'):
    ##			talk_string = 'oar'
    ##		elif(talk_string == 'to'):
    ##			talk_string = 'two'
    ##
    ##		talk_fid = open(self.talk_file,'w')
    ##		talk_fid.write(".. " + talk_string + " ?")
    ##		talk_fid.close()
    ##		os.spawnv(os.P_NOWAIT,'C:/festival/festival.exe',['festival','--tts',self.talk_file]) #"/usr/bin/festival" "c:/festival/festival.exe"

    def make_choice(self, index):
        is_undo = False
        is_equalize = False

        ## now pause (if desired)
        if self.pause_set == 1:
            self.in_pause = True
            # self.canvas.config(bg=kconfig.fill_win_color)
            self.end_pause()

        # highlight winner
        self.highlight_winner(index)

        # initialize talk string
        talk_string = ""

        # if selected a key
        if (index - kconfig.N_pred) % (kconfig.N_pred + 1) == 0:
            new_char = self.keys_li[self.index_to_wk[index]]
            # special characters
            if new_char == kconfig.space_char:
                if len(self.context) > 1:
                    talk_string = self.context
                else:
                    talk_string = "space"
                new_char = '_'
                self.old_context_li.append(self.context)
                self.context = ""
                self.last_add_li.append(1)
            elif (new_char == kconfig.mybad_char) or (new_char == kconfig.yourbad_char):
                talk_string = new_char
                # if added characters that turn
                if len(self.last_add_li) > 1:
                    last_add = self.last_add_li.pop()
                    self.context = self.old_context_li.pop()
                    if last_add > 0:  # if added text that turn
                        self.typed = self.typed[0:-last_add]
                    elif last_add == -1:  # if backspaced that turn
                        letter = self.btyped[-1]
                        self.btyped = self.btyped[0:-1]
                        self.typed += letter
                if new_char == kconfig.yourbad_char:
                    is_equalize = True
                new_char = ''
                is_undo = True
            elif new_char == kconfig.back_char:
                talk_string = new_char
                # if delete the last character that turn
                self.old_context_li.append(self.context)
                lt = len(self.typed)
                if lt > 0:  # typed anything yet?
                    self.btyped += self.typed[-1]
                    self.last_add_li.append(-1)
                    self.typed = self.typed[0:-1]
                    lt -= 1
                    if lt == 0:
                        self.context = ""
                    elif len(self.context) > 0:
                        self.context = self.context[0:-1]
                    elif not (self.typed[-1]).isalpha():
                        self.context = ""
                    else:
                        i = -1
                        while (i >= -lt) and (self.typed[i].isalpha()):
                            i -= 1
                        self.context = self.typed[i + 1:lt]
                new_char = ''
            elif new_char.isalpha():
                talk_string = new_char
                self.old_context_li.append(self.context)
                self.context += new_char
                self.last_add_li.append(1)
            else:
                if new_char == '.':
                    talk_string = "Full stop"
                else:
                    talk_string = new_char
                self.old_context_li.append(self.context)
                self.context = ""
                self.last_add_li.append(1)
            self.typed += new_char

        # if selected a word
        else:
            key = self.index_to_wk[index] / kconfig.N_pred
            pred = self.index_to_wk[index] % kconfig.N_pred
            new_word = self.words_li[key][pred]
            length = len(self.context)
            talk_string = new_word.rstrip(kconfig.space_char)  # talk string
            if length > 0:
                self.typed = self.typed[0:-length]
            self.typed += new_word
            self.last_add_li.append(len(new_word) - len(self.context))
            self.old_context_li.append(self.context)
            self.context = ""
        # update the screen
        self.draw_words()
        self.draw_typed()
        # update the word prior
        self.gen_word_prior(is_undo)

        ## talk the string
        # if self.talk_set.get() == 1:
        #     self.talk_winner(talk_string)

        # write output
        if config.is_write_data:
            self.file_handle.write("choice " + str(time.time()) + " " + str(is_undo) + " " + str(
                is_equalize) + " \"" + self.typed + "\"\n")

        return self.words_on, self.words_off, self.word_score_prior, is_undo, is_equalize

    def present_choice(self):
        print("DRAW HISTOGRAM")
        self.draw_histogram()
        # self.canvas.update_idletasks()

    def end_pause(self):
        # self.canvas.config(bg=config.bgcolor)
        self.in_pause = False
        self.on_timer()

    def quit(self, event=None):
        if not self.undefined:
            ## close clocks
            try:
                self.bc
            except AttributeError:
                bc_data = []
            else:
                bc_data = self.bc.quit()
                ## save settings
                dump_file_out = kconfig.dump_pre + "clocks." + str(self.user_id) + "." + str(
                    self.use_num) + kconfig.dump_suff
                fid = open(dump_file_out, 'w')
                cPickle.dump([self.rotate_index, bc_data], fid)
                fid.close()

            ## close write file
            if config.is_write_data:
                try:
                    self.file_handle
                except AttributeError:
                    pass
                else:
                    self.file_handle.close()

        import sys
        sys.exit()


def main():
    print "****************************\n****************************\n[Loading...]"
    app = QtGui.QApplication(sys.argv)
    screen_res = (app.desktop().screenGeometry().width(), app.desktop().screenGeometry().height())
    ex = Keyboard(key_chars, screen_res)
    sys.exit(app.exec_())

    # root = Tkinter.Tk()
    # root.title("Nomon Keyboard")
    #
    # app = Keyboard(root)
    # # root.protocol('WM_DELETE_WINDOW', app.quit)
    # # root.bind('<Control-q>', app.quit)
    # # root.bind('<Control-Q>', app.quit)
    #
    # root.mainloop()


if __name__ == "__main__":
    main()
