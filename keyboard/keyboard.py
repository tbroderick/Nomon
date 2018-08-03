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
import time
import numpy

import cPickle, pickle
from mainWindow import *
from subWindows import *
import os

sys.path.insert(0, os.path.realpath('../tests'))
from pickle_util import *

if kconfig.target_evt == kconfig.joy_evt:
    import pygame


class Keyboard(MainWindow):

    def __init__(self, screen_res, app):
        super(Keyboard, self).__init__(screen_res)

        self.app = app

        self.usenum_file = "data/usenum.pickle"
        self.usenum_handle = PickleUtil(self.usenum_file)
        self.use_num = self.usenum_handle.safe_load()
        
        if self.use_num == None:
            self.use_num = 0
        
        print "use_num is " + str(self.use_num)
        self.user_id = 0
        
        use_num = self.use_num
        user_id = self.user_id

        #This block of codes is not working 
        # check that number of arguments is valid
# =============================================================================
#         if len(sys.argv) < 3:  # replaced with a default 0 0
#             print "Error: Too few (" + str(len(sys.argv)-1) + " < 2) arguments"

#             # print "Usage: python keyboard.py user-id use-number proposed-window-width proposed-window-height"
#             # sys.exit() #replaced quit() with this
#             # quit()
#             user_id = 0
#             use_num = 0
#         # read arguments
#         else:
#             user_id = string.atoi(sys.argv[1])
#             use_num = string.atoi(sys.argv[2])
#         self.user_id = user_id
#         self.use_num = use_num
# =============================================================================
        # read extra arguments if they're there
        if len(sys.argv) > 3:
            print "this actually can happen"
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
        ####Need to see if this line works 
        if self.use_num > 0:
            # input file (if such exists) for histogram
            dump_file_in = kconfig.dump_pre + "clocks." + str(self.user_id) + "." + str(
                self.use_num - 1) + kconfig.dump_suff
            if not os.path.exists(os.path.dirname(dump_file_in)):
                os.makedirs(os.path.dirname(dump_file_in))
            dump_pickle = PickleUtil(dump_file_in)
            in_data = dump_pickle.safe_load()


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

            self.file_handle_dict['params'].append([config.period_li[config.default_rotate_ind], config.theta0])
            self.file_handle_dict['start'].append(time.time())
        else:
            self.file_handle = None
        ## set up canvas for displaying stuff
        # self.gen_canvas()
        self.gen_scale()
        # self.gen_button_frame()
        # self.toggle_pause_button()
        self.pause_set = True
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
        self.dt = dtree.DTree(train_handle, self)
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

        self.bc_init = False
        self.bars = kconfig.bars
        self.previous_undo_text = ''
        self.previous_winner=0
        self.wpm_data = config.Stack(config.wpm_history_length)
        self.wpm_time = 0
        self.clear_text = False
        self.pretrain = False

        self.initUI()

        ## set up broderclocks
        self.bc = broderclocks.BroderClocks(self, self.clock_centers, self.win_diffs, kconfig.clock_rad,
                                            self.words_on, self.words_off, kconfig.key_color,
                                            time.time(), use_num, user_id, self.time_rotate, prev_data)
        self.mainWidgit.changeValue(config.start_speed)
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

        
        
        self.gen_click_time_handle()
        ### animate ###
        self.on_timer()

        # which ones to try predicting on
        try_pred = []
        for row in range(0, self.N_rows):
            for col in range(0, self.N_keys_row[row]):
                try_pred = kconfig.key_chars[row][col].isalpha()


    #def gen_load_usenum(self):
    #    self.usenum_handle = open(self.usenum_file, 'wb')

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
                if isinstance(kconfig.key_chars[row][col], list):
                    pass
                else:
                    if kconfig.key_chars[row][col].isalpha() and (len(kconfig.key_chars[row][col]) == 1):
                        self.N_alpha_keys = self.N_alpha_keys + 1
                    elif kconfig.key_chars[row][col] == kconfig.space_char and (len(kconfig.key_chars[row][col]) == 1):
                        self.N_alpha_keys = self.N_alpha_keys + 1
                    elif kconfig.key_chars[row][col] == kconfig.break_chars[1] and (len(kconfig.key_chars[row][col]) == 1):
                        self.N_alpha_keys = self.N_alpha_keys + 1

            self.N_keys_row.append(n_keys)
            self.N_keys += n_keys
        
        print "NKEYS is " + str(self.N_keys)
        print "And N_alpha_keys is " + str(self.N_alpha_keys)
        
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
        # kconfig.N_pred = 2 # number of words per key
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
        data_file = kconfig.file_pre + str(self.user_id) + "." + str(self.use_num) + kconfig.file_stuff
        self.file_handle = PickleUtil(data_file)
        self.file_handle_dict= {'speed': [], 'params': [], 'start': [], 'press': [], 'choice':[]}


    #Pickle file to save click time
    def gen_click_time_handle(self):
        click_data_file = "data/click_time_log" + str(self.user_id) + "." + str(self.use_num) + ".pickle"
        self.click_handle = PickleUtil(click_data_file)
        

    def gen_scale(self):
        scale_length = self.w_canvas / 2  # (len(kconfig.key_chars[0])-1)*kconfig.word_w
        tick_int = int((len(config.period_li) - 1) * kconfig.word_pt * 3 / (1.0 * scale_length)) + 1
        self.time_rotate = config.period_li[self.rotate_index]

    def toggle_pause_button(self, value):
        self.pause_set = value
        self.mainWidgit.sldLabel.setFocus()

    def toggle_talk_button(self, value):
        self.talk_set = value
        self.mainWidgit.sldLabel.setFocus()  # focus on not toggle-able widget to allow keypress event

    def toggle_learn_button(self, value):
        config.is_learning = value
        self.mainWidgit.sldLabel.setFocus()  # focus on not toggle-able widget to allow keypress event

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
        self.file_handle_dict['speed'].append([time.time(), old_rotate, self.time_rotate])

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

    def init_histogram(self):
        ### histogram
        bars = self.bc.get_histogram()
        self.bars = bars

        ### undo_text
        self.undo_loc = [
            (self.N_keys_row[self.N_rows - 1] - 1) * (6 * kconfig.clock_rad + kconfig.word_w) - self.w_canvas / 2,
            2 * kconfig.clock_rad]

    def draw_histogram(self, bars=None):
        if bars == None:
            bars = self.bc.get_histogram()
        # bars = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.bars = bars
        self.mainWidgit.histogram.repaint()

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
                self.words_off.append(index)
                index += 1
            self.words_on.append(index)
            self.word_pair.append((key,))
            index += 1
        # Send words to MainKeyboardWidget
        words = []
        for letter_group in self.words_li:
            for word in letter_group:
                if word != '':
                    words += [word]
        self.word_list = words
        self.typed_versions = ['']
        
        print "THe self.words_on are " + str(self.words_on)
        print "Self.word list is " + str(self.word_list)

    def raise_words(self):
        pass


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
                self.words_off.append(index)
                index += 1
            self.words_on.append(index)
            self.word_pair.append((key,))
            index += 1
        # Send words to MainKeyboardWidget
        words = []
        for letter_group in self.words_li:
            for word in letter_group:
                if word != '':
                    words += [word]

        self.word_list = words
        self.mainWidgit.updateClocks()

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
                    if self.keys_li[key] in kconfig.break_chars[0]:
                        prob = kconfig.break_prob
                    if self.keys_li[key] == kconfig.back_char:
                        prob = kconfig.back_prob
                    if self.keys_li[key] == kconfig.clear_char:
                        prob = kconfig.undo_prob

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

    def draw_typed(self):
        self.wpm_update()

        delete = False
        undo = False
        previous_text = self.mainWidgit.text_box.toPlainText()

        if len(self.last_add_li) > 1:
            last_add = self.last_add_li[-1]
            if last_add > 0:  # typed something
                new_text = self.typed[-last_add:len(self.typed)]
                undo_text = new_text
            elif last_add == -1:  # backspace
                new_text = ''
                delete = True
                undo_text = kconfig.back_char
                last_add = 0

        else:
            new_text = ''
            undo_text = new_text
            last_add = 0


        index = self.previous_winner
        if self.mainWidgit.clocks[index] != '':
            if self.mainWidgit.clocks[index].text == kconfig.mybad_char:
                undo = True
                delete = False
        if self.typed_versions[-1] == '' and len(self.typed_versions) > 1:
            undo_text = 'Clear'

        if self.clear_text:
            self.typed_versions += ['']
            self.mainWidgit.text_box.setText('')
            self.clear_text = False
            undo_text = 'Clear'
        elif delete:

            self.prefix = self.prefix[:-1]
            if self.typed_versions[-1] != '':
                self.typed_versions += [previous_text[:-1]]
                self.mainWidgit.text_box.setText("<span style='color:#000000;'>" + self.typed_versions[-1] + "</span>")
        elif undo:
            if len(self.typed_versions) > 1:
                self.typed_versions = self.typed_versions[:-1]
                self.mainWidgit.text_box.setText("<span style='color:#000000;'>" + self.typed_versions[-1] + "</span>")
        else:
            self.typed_versions += [previous_text+new_text]
            self.mainWidgit.text_box.setText("<span style='color:#000000;'>"+previous_text+"</span><span style='color:#00dd00;'>"+new_text+"</span>")
        self.previous_undo_text = undo_text
        self.mainWidgit.undo_label.setText("<font color='green'>"+undo_text+"</font>")


    def wpm_update(self):
        time_diff = (time.time()-self.wpm_time)
        if time_diff < 15.*10/self.time_rotate:
            self.wpm_data+time_diff
            self.wpm_time = 0
            self.mainWidgit.wpm_label.setText("Selections/Min: "+str(round(self.wpm_data.average(), 2)))

    def on_pause(self):

        self.mainWidgit.pause_timer.start(kconfig.pause_length)
        self.in_pause = True
        self.setStyleSheet("background-color:"+config.bg_color_highlt+";")
        self.mainWidgit.text_box.setStyleSheet("background-color:#ffffff;")

    def end_pause(self):
        self.mainWidgit.pause_timer.stop()
        self.in_pause = False
        self.setStyleSheet("")
        self.on_timer()

    def on_timer(self):
        if self.wpm_time != 0:
            if time.time()-self.wpm_time > 15:  # reset wrd prior and click history after inactivity
                self.wpm_time = 0
                self.bc.clock_history = [[]]
                self.bc.is_undo = True
                self.bc.init_round(True, False, self.bc.prev_cscores)
                self.wpm_time = 0

        if self.focusWidget() == self.mainWidgit.text_box:
            self.mainWidgit.sldLabel.setFocus()  # focus on not toggle-able widget to allow keypress event
        if self.bc_init:
            if not self.in_pause:
                start_t = time.time()
                self.bc.increment(start_t)

    def on_press(self):
        # self.canvas.focus_set()
        if self.wpm_time == 0:
            self.wpm_time = time.time()

        if not self.in_pause:
            if config.is_write_data:
                self.num_presses += 1
                self.file_handle_dict['press'].append([time.time(), self.num_presses])
            self.bc.select(time.time())
        self.play()
    def play(self):
        sound_file = "icons/bell.wav"
        QSound(sound_file).play()

    def highlight_winner(self, index):


        if self.mainWidgit.clocks[index] != '':
            self.mainWidgit.clocks[index].selected = True
            self.mainWidgit.clocks[index].repaint()
            self.mainWidgit.highlight_timer.start(2000)

    def end_highlight(self):
        index = self.previous_winner
        if self.mainWidgit.clocks[index] != '':
            self.mainWidgit.clocks[index].selected = False
            self.mainWidgit.clocks[index].repaint()
            self.mainWidgit.highlight_timer.stop()

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
            self.on_pause()
            self.mainWidgit.pause_timer.start(kconfig.pause_length)

        # highlight winner
        self.previous_winner = index
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
            elif new_char == kconfig.mybad_char or new_char == kconfig.yourbad_char:
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
                print(self.context)
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
            elif new_char == kconfig.clear_char:
                talk_string = 'clear'

                new_char = '_'
                self.old_context_li.append(self.context)
                self.context = ""
                self.last_add_li.append(1)

                self.clear_text = True

            
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
            self.file_handle_dict['choice'].append([time.time(), is_undo, is_equalize, self.typed])

        return self.words_on, self.words_off, self.word_score_prior, is_undo, is_equalize

    def present_choice(self):
        self.draw_histogram()
        # self.canvas.update_idletasks()

    
    def closeEvent(self, event):
        print "CLOSING THRU CLOSEEVENT"
        self.quit(event)
        #self.deleteLater()
    
    
    def quit(self, event=None):
        #Save click time log 
        self.click_handle.safe_save({'user id': self.user_id, 'click time list': self.bc.click_time_list})
        self.usenum_handle.safe_save(self.use_num)
        
        bars_pickle = PickleUtil("data/barsdump.pickle")
        prev_barlist = bars_pickle.safe_load()
        if prev_barlist == None:
            prev_barlist = []



        self.pretrain_bars = self.bc.hsi.dens_li
        bars_pickle.safe_save(prev_barlist+[[self.pretrain_bars, self.bars]])
        print "click pickle closed properly!"

        if config.is_write_data:
            data_file = "data/preconfig.pickle"
            file_handle = PickleUtil(data_file)
            li = self.bc.hsi.dens_li
            z = self.bc.hsi.Z
            
            ##SO HERE IT IS PBC BUT IT SHOULD BE LIKE BC
            self.save_dict = {'li': li, 'z': z, 'opt_sig': self.bc.hsi.opt_sig, 'y_li': self.bc.hsi.y_li}
            file_handle.safe_save(self.save_dict)
            print "I'm quitting and the density is" + str(li)
            print "And the Z is " + str(z)
            print "file closed"
                  
        #Do NOT UNCOMMENT THESE
        
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
                    self.use_num) + kconfig.dump_stuff
                dump_pickle = PickleUtil(dump_file_out)
                dump_pickle.safe_save({'rotate index': self.rotate_index, 'bc data': bc_data})
                
    
            ## close write file
            #Save file_handle_dict to file_handle
            if config.is_write_data:
                try:
                    self.file_handle.safe_save(self.file_handle_dict)
                except AttributeError:
                    pass
                
        import sys
        sys.exit()
        #self.deleteLater()

    def launch_help(self):
        help_window = StartWindow(self.mainWidgit.screen_res, False)
        help_window.help_screen = True

    def launch_retrain(self):
        retrain_window = Pretraining(self.mainWidgit.screen_res, self)
        retrain_window.screen_num = 3
        retrain_window.mainWidgit.close()
        retrain_window.mainWidgit = WelcomeScreen(retrain_window)
        retrain_window.mainWidgit.initUI4()
        retrain_window.setCentralWidget(retrain_window.mainWidgit)


def main():
    print "****************************\n****************************\n[Loading...]"
    app = QtGui.QApplication(sys.argv)
    screen_res = (app.desktop().screenGeometry().width(), app.desktop().screenGeometry().height())

    splash = StartWindow(screen_res, True)
    app.processEvents()
    ex = Keyboard(screen_res, app)


    if kconfig.first_load:
        welcome = Pretraining(screen_res, ex)
        # pickle.dump(False, open("user_preferences/first_load.p", "wb"))

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
