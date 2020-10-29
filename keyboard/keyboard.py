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
from PySide2 import QtCore, QtGui, QtWidgets, QtMultimedia

from mainWindow import MainWindow
from subWindows import Pretraining, StartWindow
from phrases import Phrases
# import dtree
from kenlm_lm import LanguageModel
from pickle_util import PickleUtil
from text_stats import calc_MSD

import sys
import os
# import string
import kconfig
import config
import time
from appdirs import user_data_dir
import pathlib
from broderclocks import BroderClocks
from win_output import outputManager
import win32api, win32con

# sys.path.insert(0, os.path.realpath('../KernelDensityEstimation'))

sys._excepthook = sys.excepthook


def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook

if kconfig.target_evt == kconfig.joy_evt:
    import pygame


class Keyboard(MainWindow):

    def __init__(self, screen_res, app):
        super(Keyboard, self).__init__(screen_res)

        self.app = app
        self.is_simulation = False
        self.pretrain_window = False

        # 2 is turn fully on, 1 is turn on but reduce, 0 is turn off
        self.word_pred_on = 2
        # Number of word clocks to display in case word prediction == 1 (reduced)
        self.reduce_display = 5

        # get user data before initialization
        self.gen_data_handel()

        self.up_handel = PickleUtil(os.path.join(self.user_handel, 'user_preferences.p'))
        user_preferences = self.up_handel.safe_load()
        if user_preferences is None:
            first_load = True
            user_preferences = ['default', 1, False, 'alpha', 'off', config.default_rotate_ind, True]
            self.up_handel.safe_save(user_preferences)
        else:
            first_load = False

        self.clock_type, self.font_scale, self.high_contrast, self.layout_preference, self.pf_preference, \
            self.start_speed, self.is_write_data = user_preferences

        self.phrase_prompts = False  # set to true for data collection mode

        if self.phrase_prompts:
            self.phrases = Phrases("resources/twitter-phrases/watch-combined.txt")

        else:
            self.phrases = None


        if self.layout_preference == 'alpha':
            self.target_layout = kconfig.alpha_target_layout
            self.key_chars = kconfig.key_chars
        elif self.layout_preference == 'qwerty':
            self.target_layout = kconfig.qwerty_target_layout
            self.key_chars = kconfig.key_chars
        elif self.layout_preference == 'emoji':
            self.target_layout = kconfig.emoji_target_layout
            self.key_chars = kconfig.emoji_keys
            self.word_pred_on = 0

        # set up dictionary tree
        # splash = StartWindow(screen_res, True)
        self.pause_animation = False

        self.output_manager = outputManager()
        self.is_output_text = False

        self.lm_prefix = ""
        self.left_context = ""

        self.cwd = os.getcwd()

        word_lm_path = os.path.join(os.path.join(self.cwd, 'resources'),
                                    'mix4_opt_min_lower_100k_4gram_2.5e-9_prob8_bo4_compress255.kenlm')
        char_lm_path = os.path.join(os.path.join(self.cwd, 'resources'),
                                    'mix4_opt_min_lower_12gram_6e-9_prob9_bo4_compress255.kenlm')
        vocab_path = os.path.join(os.path.join(self.cwd, 'resources'), 'vocab_lower_100k.txt')
        char_path = os.path.join(os.path.join(self.cwd, 'resources'), 'char_set.txt')

        self.lm = LanguageModel(word_lm_path, char_lm_path, vocab_path, char_path)

        # initialize pygame and joystick
        if kconfig.target_evt is kconfig.joy_evt:
            pygame.init()
            if pygame.joystick.get_count() < 1:
                # no joysticks found
                print("Please connect a joystick.\n")
                self.quit(None)
            else:
                # create a new joystick object from
                # ---the first joystick in the list of joysticks
                Joy0 = pygame.joystick.Joystick(0)
                # tell pygame to record joystick events
                Joy0.init()
            # start looking for events
            self.parent.after(0, self.find_events)
        # not in selection pause
        self.in_pause = False

        # determine keyboard positions
        self.init_locs()
        # get old data if there is such
        # Just for default. Loaded again when bc initializes
        self.rotate_index = config.default_rotate_ind
        # set up file handle for printing useful stuff
        self.undefined = False

        self.params_handle_dict = {'speed': [], 'params': [], 'start': [], 'press': [], 'choice': []}
        self.num_presses = 0

        self.params_handle_dict['params'].append([config.period_li[config.default_rotate_ind], config.theta0])
        self.params_handle_dict['start'].append(time.time())

        self.gen_scale()
        self.pause_set = True
        # set up "typed" text
        self.typed = ""
        self.btyped = ""
        self.context = ""
        self.old_context_li = [""]
        self.last_add_li = [0]
        # set up "talked" text
        # self.talk_file = "talk.txt"
        self.sound_set = True
        self.press_lock = False
        self.press_lock_status = False

        # check for speech
        # talk_fid = open(self.talk_file, 'wb')
        # write words
        self.init_words()

        self.bars = kconfig.bars

        self.bc_init = False

        self.previous_undo_text = ''
        self.previous_winner = 0

        self.wpm_data = []
        self.decay_avg_wpm = 0
        self.wpm_time = 0
        self.error_data = []
        self.decay_avg_error = 1

        self.clear_text = False
        self.pretrain = False

        self.emoji_box_highlight = [-1, -1]
        self.init_ui()

        self.mainWidget.clockgrid_widget.update_word_clocks(self.words_li)

        sound_file = "icons/bell.wav"
        self.sound_player = QtMultimedia.QSound(sound_file)

        self.time_rotate = config.period_li[self.start_speed]
        # get language model results
        self.gen_word_prior(False)

        self.clock_spaces = np.zeros((len(self.clock_centers), 2))

        self.bc = BroderClocks(self)
        self.mainWidget.change_value(self.start_speed)

        self.bc.init_follow_up(self.word_score_prior)

        # draw histogram
        self.init_histogram()

        self.save_environment()

        self.consent = False

        if first_load:
            self.pretrain = True
            self.welcome = Pretraining(self, screen_res)


        # animate

        # record to prevent double tap
        self.last_key_press_time = time.time()
        self.last_release_time = time.time()

        self.update_radii = False
        self.on_timer()

    def gen_data_handel(self):
        self.cwd = os.getcwd()
        self.data_path = user_data_dir('data', 'Nomon')
        if os.path.exists(self.data_path):
            user_files = list(os.walk(self.data_path))
            users = user_files[0][1]
        else:
            pathlib.Path(self.data_path).mkdir(parents=True, exist_ok=True)
            user_files = None
            users = []
        input_method = 'text'
        if user_files is not None and len(users) != 0:
            message = QtWidgets.QMessageBox()
            message.setText("You can either create a new user profile or "
            "load an existing user profile.")
            message.setWindowTitle("Load User")
            message.addButton('Create New User', QtWidgets.QMessageBox.YesRole)
            message.addButton('Load Previous User', QtWidgets.QMessageBox.NoRole)
            message.setDefaultButton(QtWidgets.QMessageBox.Yes)
            response = message.exec_()
            if response == 0:
                input_method = 'text'
            else:
                input_method = 'list'

        if input_method == 'text':
            valid_user_id = False
            input_text = "Please input a Number that will be used to save your user information"
            while not valid_user_id:
                num, ok = QtWidgets.QInputDialog.getInt(self, "User ID Number Input", input_text)
                if str(num) not in users:
                    valid_user_id = True
                else:
                    input_text = "The user ID you inputed already exists! \n please input a valid user ID or press " \
                                 "\"cancel\" to choose an existing one from a list"
                if ok == 0:
                    input_method = 'list'
                    break
            if input_method == 'text':
                self.user_id = num
                user_id_path = os.path.join(self.data_path, str(self.user_id))
                os.mkdir(user_id_path)

        if input_method == 'list':
            item, ok = QtWidgets.QInputDialog.getItem(self, "Select User ID", "List of save User IDs:", users, 0, False)
            self.user_id = item


        self.user_handel = os.path.join(self.data_path, str(self.user_id))
        user_id_files = list(os.walk(self.user_handel))
        user_id_calibrations = user_id_files[0][1]
        if len(user_id_calibrations) == 0:
            self.data_handel = os.path.join(self.user_handel, 'cal0')
            os.mkdir(self.data_handel)
            user_id_cal_files = None
            self.user_cal_num = 0
        else:
            user_id_cal_files = user_id_files[-1][2]
            self.data_handel = user_id_files[-1][0]
            self.user_cal_num = len(user_id_calibrations)-1
        if user_id_cal_files is not None:
            self.use_num = sum([1 if 'params_data' in file_name else 0 for file_name in user_id_cal_files])
        else:
            self.use_num = 0
        print(self.data_handel)

    def save_environment(self):
        self.rotate_index_past = self.rotate_index
        self.window_size_past = self.frameGeometry()
        self.clock_type_past = self.clock_type
        self.layout_preference_past = self.layout_preference
        self.high_contrast_past = self.high_contrast

    def data_auto_save(self):
        if len(self.bc.click_time_list) > 0:
            print("auto saving data")
            self.bc.save_when_quit()

    def find_events(self):
        # check everything in the queue of pygame events
        events = pygame.event.get()
        for event in events:
            # event type for pressing any of the joystick buttons down
            if event.type == pygame.JOYBUTTONDOWN:
                # generate the event I've defined
                self.canvas.event_generate(kconfig.joy_evt)

        # return to check for more events in a moment
        self.parent.after(20, self.find_events)

    def keyPressEvent(self, e):

        # if e.key() == QtCore.Qt.Key_Space:
        #     if self.press_lock:
        #         if not self.press_lock_status:
        #             self.on_press()
        #             self.press_lock_status = True
        #     else:
        #         self.on_press()

        if e.key() == QtCore.Qt.Key_Control:
            if self.press_lock:
                if self.press_lock_status:
                    self.press_lock_status = False

        if e.key() == QtCore.Qt.Key_Return:
            if self.phrase_prompts:
                if len(self.typed_versions) > 0:
                    self.update_phrases(self.typed_versions[-1], "",  next_phrase=True)
                else:
                    self.update_phrases("", "", next_phrase=True)

    def init_locs(self):
        # size of keyboard
        key_chars = kconfig.key_chars

        self.N_rows = len(key_chars)
        self.N_keys_row = []
        self.N_keys = 0
        self.N_alpha_keys = 0

        for row in range(self.N_rows):
            n_keys = len(key_chars[row])

            for col in range(n_keys):
                if not isinstance(key_chars[row], list):
                    if (key_chars[row][col] in kconfig.main_chars and (len(key_chars[row]) == 1)):
                        self.N_alpha_keys = self.N_alpha_keys + 1

                    elif ((key_chars[row] == kconfig.space_char) and (len(key_chars[row]) == 1)):
                        self.N_alpha_keys = self.N_alpha_keys + 1

                    elif (key_chars[row] == kconfig.break_chars[1] and (len(key_chars[row]) == 1)):
                        self.N_alpha_keys = self.N_alpha_keys + 1

            self.N_keys_row.append(n_keys)
            self.N_keys += n_keys


        # print "NKEYS is " + str(self.N_keys)
        # print "And N_alpha_keys is " + str(self.N_alpha_keys)

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
                # predictive words
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
                self.rect_locs.append([x + rect_offset, y, x + rect_end, y + 2 * kconfig.clock_rad])
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
                key_char = key_chars[row][col]
                self.keys_li.append(key_chars[row][col])
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

    def gen_scale(self):
        scale_length = self.w_canvas / 2  # (len(kconfig.key_chars[0])-1)*kconfig.word_w
        tick_int = int((len(config.period_li) - 1) * kconfig.word_pt * 3 / (1.0 * scale_length)) + 1
        self.time_rotate = config.period_li[self.rotate_index]

    def toggle_pause_button(self, value):
        self.pause_set = value
        self.mainWidget.sldLabel.setFocus()

    def toggle_sound_button(self, value):
        self.sound_set = value
        self.mainWidget.sldLabel.setFocus()

    def toggle_talk_button(self, value):
        self.talk_set = value
        self.mainWidget.sldLabel.setFocus()  # focus on not toggle-able widget to allow keypress event

    def toggle_learn_button(self, value):
        config.is_learning = value
        self.mainWidget.sldLabel.setFocus()  # focus on not toggle-able widget to allow keypress event

    def change_speed(self, index):
        # speed (as shown on scale)
        speed_index = int(index)
        # period (as stored in config.py)
        self.rotate_index = speed_index
        old_rotate = self.time_rotate
        self.time_rotate = config.period_li[self.rotate_index]
        self.bc.clock_inf.clock_util.change_period(self.time_rotate)

        # note period change in log file
        self.params_handle_dict['speed'].append([time.time(), old_rotate, self.time_rotate])

        # update the histogram
        self.draw_histogram()

    def init_histogram(self):
        # histogram
        bars = self.bc.get_histogram()
        self.bars = bars

        # undo_text
        self.undo_loc = [
            (self.N_keys_row[self.N_rows - 1] - 1) * (6 * kconfig.clock_rad + kconfig.word_w) - self.w_canvas / 2,
            2 * kconfig.clock_rad]

    def draw_histogram(self, bars=None):
        if bars == None:
            bars = self.bc.get_histogram()
        # bars = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.bars = bars
        self.mainWidget.histogram.update()

    def init_words(self):
        if self.word_pred_on == 1:
            num_words_total = 5
        elif self.word_pred_on == 0:
            num_words_total = 0
        else:
            num_words_total = kconfig.num_words_total
        (self.words_li, self.word_freq_li, self.key_freq_li) = self.lm.get_words(self.left_context, self.context,
                                                                                 self.keys_li,
                                                                                 num_words_total=num_words_total)
        if self.layout_preference == "emoji":
            self.key_freq_li = np.array([np.log(1/len(self.key_chars)) for i in range(len(self.key_chars))])

        self.word_id = []
        self.word_pair = []
        word = 0
        index = 0
        windex = 0
        self.words_on = []
        self.words_off = []
        self.word_list = []
        # self.flag_args = []

        temp_word_list = [word_item for sublist in self.words_li for word_item in sublist]
        for word_item in temp_word_list:
            if word_item != '':
                self.word_list.append(word_item)

        # print "TURNED ON AND WORD LIST IS" + str(self.word_list)

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


                windex += 1
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
        self.typed_versions = ['']


    def draw_words(self):
        if self.word_pred_on == 1:
            num_words_total = 5
        elif self.word_pred_on == 0:
            num_words_total = 0
        else:
            num_words_total = kconfig.num_words_total
        (self.words_li, self.word_freq_li, self.key_freq_li) = self.lm.get_words(self.left_context, self.context, self.keys_li, num_words_total=num_words_total)

        self.mainWidget.clockgrid_widget.update_word_clocks(self.words_li)

        if self.layout_preference == "emoji":
            self.key_freq_li = np.array([np.log(1/len(self.key_chars)) for i in range(len(self.key_chars))])

        word = 0
        index = 0
        self.words_on = []
        self.words_off = []
        self.word_list = []


        temp_word_list = [word_item for sublist in self.words_li for word_item in sublist]
        for word_item in temp_word_list:
            if word_item != '' and all(c in "abcdefghijklmnopqrstuvwxyz\' " for c in word_item):
                self.word_list.append(word_item)

        len_con = len(self.context)

        windex = 0
        for key in range(0, self.N_alpha_keys):
            for pred in range(0, kconfig.N_pred):
                word_str = self.words_li[key][pred]
                len_word = len(word_str)
                if len_con > 1 and len_word > kconfig.max_chars_display:
                    word_str = "+" + word_str[len_con:len_word]
                if word_str == '':
                    self.words_off.append(index)
                else:

                    self.words_on.append(index)


                windex += 1
                word += 1
                index += 1
            self.words_on.append(index)

            self.word_pair.append((key,))
            index += 1
        for key in range(self.N_alpha_keys, self.N_keys):
            for pred in range(0, kconfig.N_pred):
                self.word_pair.append((key, pred))
                self.words_off.append(index)
                index += 1
            self.words_on.append(index)
            self.word_pair.append((key,))
            index += 1


    def gen_word_prior(self, is_undo):
        self.word_score_prior = []
        N_on = len(self.words_on)
        if not is_undo:
            for index in self.words_on:
                pair = self.word_pair[index]
                # word case
                if len(pair) == 2:
                    (key, pred) = pair
                    prob = self.word_freq_li[key][pred] + np.log(kconfig.rem_prob)
                    self.word_score_prior.append(prob)
                else:
                    key = pair[0]
                    prob = self.key_freq_li[key]
                    prob = prob + np.log(kconfig.rem_prob)
                    if self.keys_li[key] == kconfig.mybad_char or self.keys_li[key] == kconfig.yourbad_char:
                        prob = np.log(kconfig.undo_prob)
                    # if self.keys_li[key] in kconfig.break_chars:
                    #     prob = np.log(kconfig.break_prob)
                    if self.keys_li[key] == kconfig.back_char:
                        prob = np.log(kconfig.back_prob)
                    if self.keys_li[key] == kconfig.clear_char:
                        prob = np.log(kconfig.undo_prob)
                    if self.keys_li[key] == kconfig.speak_char:
                        prob = np.log(kconfig.undo_prob)

                    self.word_score_prior.append(prob)
        else:
            for index in self.words_on:
                pair = self.word_pair[index]
                if len(pair) == 1:
                    key = pair[0]
                    if (self.keys_li[key] == kconfig.mybad_char) or (self.keys_li[key] == kconfig.yourbad_char):
                        prob = kconfig.undo_prob
                        self.word_score_prior.append(np.log(prob))
                    else:
                        self.word_score_prior.append(-float("inf"))
                else:
                    self.word_score_prior.append(-float("inf"))

    def reset_context(self):
        self.left_context = ""
        self.context = ""
        self.typed = ""
        self.lm_prefix = ""
        self.draw_words()

    def update_phrases(self, cur_text, input_text, next_phrase=False):
        cur_phrase_typed, _ = self.phrases.compare(cur_text)
        cur_phrase_highlighted = self.phrases.highlight(cur_text)

        if next_phrase:
            if len(cur_text+input_text) > 0:
                self.text_stat_update(self.phrases.cur_phrase, self.typed_versions[-1])

            self.typed_versions = ['']
            self.mainWidget.text_box.setText('')
            self.mainWidget.speed_slider.setEnabled(True)
            self.mainWidget.speed_slider_label.setStyleSheet('QLabel { color: blue }')
            self.mainWidget.sldLabel.setStyleSheet('QLabel { color: blue }')

            self.clear_text = False
            undo_text = 'Clear'

            self.phrases.sample()
            input_text = ""
            cur_phrase_highlighted = self.phrases.highlight("")
            self.reset_context()

            if self.is_write_data:
                choice_dict = {"time": time.time(), "undo": False, "backspace": False, "typed": "", "target": self.phrases.cur_phrase}
                self.params_handle_dict['choice'].append(choice_dict)

        self.mainWidget.text_box.setText(
            "<p>" + cur_phrase_highlighted + "<\p><p>" + input_text + "</span><\p>")

        if self.layout_preference == 'emoji':
            if len(self.phrases.cur_phrase) > len(cur_text):
                target_emoji = self.phrases.cur_phrase[len(cur_text)]
                self.emoji_box_highlight = np.where(np.array(self.target_layout[:-1]) == target_emoji)
            else:
                self.emoji_box_highlight = [-1, -1]
            self.mainWidget.update()
            # next_emoji_clock = self.mainWidget.clockgrid_widget.clocks[4*key_index+3]

    def draw_typed(self):
        new_text = ''
        redraw_words = False
        # phrases

        delete = False
        undo = False
        undo_text = ""
        if self.phrase_prompts:
            previous_text = self.mainWidget.text_box.toPlainText().split("\n")[-1]
        else:
            previous_text = self.mainWidget.text_box.toPlainText()

        if len(previous_text) > 0 and previous_text[-1] == "_":
            previous_text = previous_text[:-1] + " "

        if len(self.last_add_li) > 1:
            last_add = self.last_add_li[-1]
            if last_add > 0:  # typed something
                new_text = self.typed[-last_add:len(self.typed)]

                undo_text = new_text
            elif last_add == -1:  # backspace
                new_text = ''
                delete = True
                undo_text = kconfig.back_char
        else:
            new_text = ''
            undo_text = new_text

        if new_text in [". ",", ","? ", "! "]:
            previous_text = previous_text[:-1]
            redraw_words  = True

        index = self.previous_winner
        if self.mainWidget.clockgrid_widget.clocks[index] != '':
            if self.mainWidget.clockgrid_widget.clocks[index].text in [kconfig.mybad_char, 'Undo']:
                undo = True
                delete = False
        if self.typed_versions[-1] == '' and len(self.typed_versions) > 1:
            undo_text = 'Clear'

        if self.clear_text:
            if self.is_output_text:
                self.output_manager.remove_text(len(self.typed_versions[-1]))
            self.typed_versions += ['']
            input_text = ""
            self.lm_prefix = ""
            self.mainWidget.text_box.setText('')
            self.clear_text = False
            undo_text = 'Clear'

        elif delete:
            # self.prefix = self.prefix[:-1]
            if self.typed_versions[-1] != '':
                self.typed_versions += [previous_text[:-1]]
                new_text = self.typed_versions[-1]
                if len(new_text) > 0 and new_text[-1] == " ":
                    new_text = new_text[:-1] + "_"

                input_text = "<span style='color:#000000;'>" + new_text + "</span>"
                self.mainWidget.text_box.setText("<span style='color:#000000;'>" + new_text + "</span>")

                if self.is_output_text:
                    self.output_manager.type_text(kconfig.back_char)
            else:
                input_text = ""
        elif undo:
            if len(self.typed_versions) > 1:
                if self.is_output_text:
                    cur_length = len(self.typed_versions[-1])
                    prev_length = len(self.typed_versions[-2])
                    if prev_length > cur_length:
                        text_diff_length = prev_length - cur_length
                        text_diff = self.typed_versions[-2][-text_diff_length:]
                        self.output_manager.type_text(text_diff)
                    else:
                        if cur_length >= 2 and self.typed_versions[-1][-2:] in ["? ", "! ", ", ", ". "]:
                            self.output_manager.type_text(kconfig.back_char+kconfig.back_char+" ")
                        else:
                            self.output_manager.remove_text(cur_length - prev_length)

                self.typed_versions = self.typed_versions[:-1]

                new_text = self.typed_versions[-1]

                if len(new_text) > 0 and new_text[-1] == " ":
                    new_text = new_text[:-1] + "_"

                input_text = "<span style='color:#000000;'>" + new_text + "</span>"
                self.mainWidget.text_box.setText("<span style='color:#000000;'>" + new_text + "</span>")
            else:
                input_text = ""
        else:
            self.typed_versions += [previous_text + new_text]

            if self.is_output_text:
                text_to_output = new_text
                for break_char in kconfig.break_chars:
                    text_to_output = text_to_output.replace(break_char+" ", kconfig.back_char+break_char+" ")
                self.output_manager.type_text(text_to_output)

            if len(new_text) > 0 and new_text[-1] == " ":
                new_text = new_text[:-1] + "_"

            input_text = "<span style='color:#000000;'>" + previous_text + "</span><span style='color:#0000dd;'>"\
                         + new_text + "</span>"


            self.mainWidget.text_box.setText(
                "<span style='color:#000000;'>" + previous_text + "</span><span style='color:#0000dd;'>"
                + new_text + "</span>")

        if undo_text == kconfig.mybad_char:
            undo_text = "Undo"
        elif undo_text == kconfig.back_char:
            undo_text = "Backspace"
        elif undo_text == kconfig.clear_char:
            undo_text = "Clear"

        self.previous_undo_text = undo_text
        self.mainWidget.undo_label.setText("<font color='green'>" + undo_text + "</font>")

        if self.phrase_prompts:
            self.update_phrases(self.typed_versions[-1], input_text)

    def text_stat_update(self, phrase, typed):

        _, cur_error = calc_MSD(phrase, typed)

        self.error_data = [cur_error] + self.error_data
        decaying_weights = np.power(0.8, np.arange(len(self.error_data)))
        decaying_weights /= np.sum(decaying_weights)

        decay_avg_error = sum(np.array(self.error_data)*decaying_weights)
        error_delta = decay_avg_error / (self.decay_avg_error + 0.000001)
        self.decay_avg_error = decay_avg_error

        self.wpm_data = [(len(typed.split(" "))-1) / (time.time() - self.wpm_time)*60] + self.wpm_data
        self.wpm_time = 0
        decaying_weights = np.power(0.8, np.arange(len(self.wpm_data)))
        decaying_weights /= np.sum(decaying_weights)

        decay_avg_wpm = sum(np.array(self.wpm_data) * decaying_weights)
        wpm_delta = decay_avg_wpm / (self.decay_avg_wpm + 0.000001)
        self.decay_avg_wpm = decay_avg_wpm

        if error_delta > 1:
            error_red = int(min(4, error_delta)*63)
            error_green = 0
        else:
            error_green = int(min(4, 1/error_delta) * 63)
            error_red = 0

        if wpm_delta < 1:
            wpm_red = int(min(4, wpm_delta)*63)
            wpm_green = 0
        else:
            wpm_green = int(min(4, 1/wpm_delta) * 63)
            wpm_red = 0


        self.mainWidget.error_label.setStyleSheet("color: rgb("+str(error_red)+", "+str(error_green)+", 0);")

        self.mainWidget.wpm_label.setStyleSheet("color: rgb(" + str(wpm_red) + ", " + str(wpm_green) + ", 0);")

        self.mainWidget.error_label.setText("Error Rate: " + str(round(decay_avg_error, 2)))
        self.mainWidget.wpm_label.setText("Words/Min: " + str(round(decay_avg_wpm, 2)))

    def on_pause(self):
        self.mainWidget.pause_timer.start(kconfig.pause_length)
        self.in_pause = True
        self.mainWidget.keygrid_widget.highlight = True
        self.mainWidget.keygrid_widget.update()


    def end_pause(self):
        self.mainWidget.pause_timer.stop()
        self.in_pause = False
        self.mainWidget.keygrid_widget.highlight = False
        self.mainWidget.keygrid_widget.update()
        self.on_timer()

    def on_timer(self):
        if self.focusWidget() == self.mainWidget.text_box:
            self.mainWidget.sldLabel.setFocus()  # focus on not toggle-able widget to allow keypress event

        if self.bc_init:
            self.bc.clock_inf.clock_util.increment(self.words_on)

        is_input = win32api.GetAsyncKeyState(win32con.VK_SPACE)
        if is_input:
            if not self.output_manager.ignore_keyevent:
                win32api.keybd_event(0x20, 0, win32con.KEYEVENTF_KEYUP, 0)
                if self.is_output_text:
                    win32api.keybd_event(0x08, 0, 0, 0)
                    win32api.keybd_event(0x08, 0, win32con.KEYEVENTF_KEYUP, 0)
                if not self.pretrain:
                    self.on_press()
            else:
                self.output_manager.ignore_keyevent = False

    def on_press(self):

        if time.time() - self.last_key_press_time > 1:
            self.last_key_press_time = time.time()
            # self.canvas.focus_set()
            if self.wpm_time == 0:
                self.wpm_time = time.time()

            if self.sound_set:
                self.play()

            if self.phrase_prompts:
                self.mainWidget.speed_slider.setEnabled(False)
                self.mainWidget.speed_slider_label.setStyleSheet('QLabel { color: grey }')
                self.mainWidget.sldLabel.setStyleSheet('QLabel { color: grey }')

            if self.is_write_data:
                self.num_presses += 1

            self.bc.select()


    def play(self):

        self.sound_player.play()

    def highlight_winner(self, index):
        if self.mainWidget.clockgrid_widget.clocks[index] != '':
            self.mainWidget.clockgrid_widget.clocks[index].selected = True
            self.mainWidget.highlight_timer.start(kconfig.pause_length)

    def end_highlight(self):
        index = self.previous_winner

        if self.mainWidget.clockgrid_widget.clocks[index] != '':
            self.mainWidget.clockgrid_widget.clocks[index].selected = False
            self.mainWidget.highlight_timer.stop()

    def talk_winner(self, talk_string):
        pass

    def make_choice(self, index):
        is_undo = False
        is_equalize = False
        is_backspace = False

        # now pause (if desired)
        if self.pause_set == 1:
            self.on_pause()
            self.mainWidget.pause_timer.start(kconfig.pause_length)

        # highlight winner
        self.previous_winner = index
        self.highlight_winner(index)

        # initialize talk string
        talk_string = ""

        # if selected a key
        if (index - kconfig.N_pred) % (kconfig.N_pred + 1) == 0:
            new_char = self.keys_li[self.index_to_wk[index]]

            # special characters
            if new_char == kconfig.speak_char:
                new_char = ""

                if len(self.typed_versions) > 0:
                    text_to_speak = self.typed_versions[-1]
                    text_to_speak = text_to_speak.replace("_", " ")
                else:
                    text_to_speak = ""

                self.output_manager.speak_text(text_to_speak)
                self.old_context_li.append(self.context)
                self.context = ""
                self.last_add_li.append(0)
            elif new_char == kconfig.space_char:
                if len(self.context) > 1:
                    talk_string = self.context
                else:
                    talk_string = "space"

                new_char = ' '
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
                is_backspace = True
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

                self.reset_context()

                self.clear_text = True

            elif new_char.isalpha() or new_char == "'" or new_char in kconfig.emoji_keys:
                talk_string = new_char
                self.old_context_li.append(self.context)
                self.context += new_char
                self.last_add_li.append(1)

            if new_char in [".", ",", "?", "!"]:
                talk_string = "Full stop"
                self.old_context_li.append(self.context)
                self.context = ""
                self.typed += new_char
                if " "+new_char in self.typed:
                    self.last_add_li.append(2)
                self.typed = self.typed.replace(" "+new_char, new_char+" ")
            else:
                self.typed += new_char

        # if selected a word
        else:
            key = self.index_to_wk[index] // kconfig.N_pred
            pred = self.index_to_wk[index] % kconfig.N_pred
            new_word = self.words_li[key][pred]
            new_selection = new_word
            length = len(self.context)
            talk_string = new_word.rstrip(kconfig.space_char)  # talk string
            if length > 0:
                self.typed = self.typed[0:-length]
            self.typed += new_word
            self.last_add_li.append(len(new_word) - len(self.context))
            self.old_context_li.append(self.context)
            self.context = ""

        # update the screen
        if self.context != "":
            self.left_context = self.typed[:-len(self.context)]
        else:
            self.left_context = self.typed

        # write output
        if self.is_write_data:
            choice_dict = {"time": time.time(), "undo": is_undo, "backspace": is_backspace, "typed": self.typed}
            if self.phrase_prompts:
                choice_dict["target"] = self.phrases.cur_phrase

            self.params_handle_dict['choice'].append(choice_dict)

        self.draw_words()
        self.draw_typed()
        # update the word prior
        self.gen_word_prior(is_undo)


        # # talk the string
        # if self.talk_set.get() == 1:
        #     self.talk_winner(talk_string)
        return self.words_on, self.words_off, self.word_score_prior, is_undo, is_equalize


    def present_choice(self):
        self.draw_histogram()
        # self.canvas.update_idletasks()

    def closeEvent(self, event):
        print("CLOSING THRU CLOSEEVENT")
        self.quit(event)
        # self.deleteLater()

    def quit(self, event=None):
        self.bc.quit_bc()
        self.close()

    def launch_help(self):
        help_window = Pretraining(self, self.mainWidget.screen_res, help_screen=True)
        help_window.show()

        self.pretrain = True
        self.mainWidget.repaint()

    def launch_retrain(self):
        retrain_window = Pretraining(self, self.mainWidget.screen_res)
        retrain_window.screen_num = 3
        retrain_window.next_screen()
        retrain_window.show()
        # retrain_window.setCentralWidget(retrain_window.mainWidget)

        retrain_window.retrain = True
        self.pretrain = True
        self.mainWidget.update()


def main():
    print("****************************\n****************************\n[Loading...]")

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    screen_res = (app.desktop().screenGeometry().width(), app.desktop().screenGeometry().height())

    # splash = StartWindow(screen_res, True)
    app.processEvents()
    ex = Keyboard(screen_res, app)

    # if first_load:
    #     ex.first_load = True
    #     welcome = Pretraining(screen_res, ex)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
