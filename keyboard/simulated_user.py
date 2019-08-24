#!/usr/bin/python

######################################
#    Copyright 2009 Tamara Broderick
#    This file is part of Nomon SimulatedUser.
#
#    Nomon SimulatedUser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Nomon SimulatedUser is distributed in the hope that it will be useful,dfg
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Nomon SimulatedUser.  If not, see <http://www.gnu.org/licenses/>.
######################################
import numpy as np
# from matplotlib import pyplot as plt

from phrases import Phrases
# import dtree
from kenlm_lm import LanguageModel
from pickle_util import PickleUtil

import sys
import os
# import string
import kconfig
import config
# from appdirs import user_data_dir
from broderclocks import BroderClocks

sys.path.insert(0, os.path.realpath('../KernelDensityEstimation'))

# sys._excepthook = sys.excepthook


class Time:
    def __init__(self, parent):
        self.parent = parent
        self.cur_time = 0
        self.update_fp_time()

    def time(self):
        return self.cur_time

    def set_time(self, t):
        if t > self.next_fp_time:
            self.cur_time = self.next_fp_time
            self.update_fp_time()
            self.parent.gen_false_positive(t)

        else:
            self.cur_time = t

    def update_fp_time(self):
        if self.parent.false_positive_rate == 0:
            self.next_fp_time = float("inf")
        else:
            self.next_fp_time = self.cur_time + np.random.exponential(scale=1 / self.parent.false_positive_rate, size=1)[0]
        # print(self.next_fp_time)


class SimulatedUser:
    def __init__(self, cwd=os.getcwd(), job_num=None, sub_call=False):

        self.is_simulation = True

        if not sub_call:
            click_dist = np.zeros(80)
            click_dist[40] = 1
            self.click_dist = list(click_dist)

        self.job_num = job_num
        self.plot = None


        self.working_dir=cwd

        if not sub_call:
            self.N_pred = kconfig.N_pred
            self.prob_thres = kconfig.prob_thres
            self.num_words_total = 26*self.N_pred
            self.lm_left_context = True
            self.win_diff_base = config.win_diff_base
            self.rotate_index = config.default_rotate_ind
            self.time_rotate = config.period_li[self.rotate_index]
            self.phrases = Phrases("resources/comm2.dev")
            self.easy_phrase = 1
            self.false_positive_rate = 0.01
            self.num_fp = 0

            self.cwd = os.getcwd()
            lm_path = os.path.join(os.path.join(self.cwd, 'resources'), 'lm_word_medium.kenlm')
            vocab_path = os.path.join(os.path.join(self.cwd, 'resources'), 'vocab_100k')

            self.lm = LanguageModel(lm_path, vocab_path, parent=self)

        self.time = Time(self)
        self.prev_time = 0

        # 2 is turn fully on, 1 is turn on but reduce, 0 is turn off
        self.word_pred_on = 2
        # Number of word clocks to display in case word prediction == 1 (reduced)
        self.reduce_display = 5

        # # get user data before initialization
        # self.gen_data_handel()

        user_preferences = ['default', 1, False, 'alpha', 'off', 12, False]

        self.clock_type, self.font_scale, self.high_contrast,self.layout_preference, self.pf_preference, \
            self.start_speed, self.is_write_data = user_preferences

        self.phrase_prompts = False  # set to true for data collection mod

        self.key_chars = kconfig.key_chars

        # set up dictionary tree
        # splash = StartWindow(screen_res, True)
        self.pause_animation = False

        self.lm_prefix = ""
        self.left_context = ""

        self.in_pause = False

        # determine keyboard positions
        self.init_locs()
        # get old data if there is such
        # Just for default. Loaded again when bc initializes
        # set up file handle for printing useful stuff
        self.undefined = False

        self.gen_scale()
        self.pause_set = True
        # set up "typed" text
        self.typed = ""
        self.btyped = ""
        self.context = ""
        self.old_context_li = [""]
        self.last_add_li = [0]

        self.sound_set = True

        self.init_words()

        self.bars = kconfig.bars

        self.bc_init = False

        self.previous_undo_text = ''
        self.previous_winner = 0
        # self.wpm_data = config.Stack(config.wpm_history_length)
        self.wpm_time = 0
        self.clear_text = False
        self.pretrain = False

        # get language model results
        self.gen_word_prior(False)

        self.clock_spaces = np.zeros((len(self.clock_centers), 2))

        self.bc = BroderClocks(self)

        self.bc.init_follow_up(self.word_score_prior)

        self.clock_params = np.zeros((len(self.clock_centers), 8))

        self.consent = False

    def init_sim_data(self):
        # self.init_clocks()
        self.num_selections = 0
        self.sel_per_min = []

        self.num_chars = 0
        self.char_per_min = []

        self.num_words = 0

        self.num_presses = 0
        self.press_per_sel = []
        self.press_per_char = []
        self.press_per_word = []

        self.num_errors = 0
        self.error_rate_avg = []
        self.kde_errors = []
        self.kde_errors_avg = None

        self.update_radii = False
        # self.on_timer()
        self.winner = False
        self.winner_text = ""

    def parameter_metrics(self, parameters, num_clicks=500, trials=1, attribute=None):
        self.init_sim_data()
        # Load parameters or use defaults
        if "click_dist" in parameters:
            self.click_dist = parameters["click_dist"]
        else:
            click_dist = np.zeros(80)
            click_dist[40] = 1
            self.click_dist = list(click_dist)

        if "N_pred" in parameters:
            self.N_pred = parameters["N_pred"]
        else:
            self.N_pred = kconfig.N_pred

        if "prob_thresh" in parameters:
            self.prob_thres = parameters["prob_thresh"]
        else:
            self.prob_thres = kconfig.prob_thres

        if "num_words" in parameters:
            self.num_words_total = parameters["num_words"]
        else:
            self.num_words_total = 26*self.N_pred

        if "num_words" in parameters:
            self.num_words_total = parameters["num_words"]
        else:
            self.num_words_total = 26*self.N_pred

        if "left_context" in parameters:
            self.lm_left_context = parameters["left_context"]
        else:
            self.lm_left_context = True

        if "win_diff" in parameters:
            self.win_diff_base = parameters["win_diff"]
        else:
            self.win_diff_base = config.win_diff_base

        if "time_rotate" in parameters:
            self.rotate_index = parameters["time_rotate"]
            self.time_rotate = config.period_li[self.rotate_index]
            self.change_speed()
        else:
            self.rotate_index = config.default_rotate_ind
            self.time_rotate = config.period_li[self.rotate_index]

        if "corpus" in parameters:
            self.phrases = Phrases(parameters["corpus"])
            self.easy_phrase = parameters["corpus"] == "resources/comm2.dev"
        else:
            self.phrases = Phrases("resources/comm2.dev")
            self.easy_phrase = 1

        if "false_positive" in parameters:
            self.false_positive_rate = parameters["false_positive"]
        else:
            self.false_positive_rate = 0.01

        self.gen_data_dir()
        for trial in range(trials):
            self.__init__(sub_call=True)

            while self.num_presses < num_clicks:
                text = self.phrases.sample()
                # print("New Phrase: \"" + text + "\"")
                self.type_text(text, verbose=False)
                # print(round(self.num_presses/num_clicks*100), " %")
                self.typed = ""  # reset tracking and context for lm -- new sentence
                self.num_words += len(text.split(" "))

            print("selections per minute: ", self.num_selections / (self.time.time() / 60))
            print("characters per minute: ", self.num_chars / (self.time.time() / 60))
            print("presses per selection: ", self.num_presses / (self.num_selections + 1))
            print("presses per character: ", self.num_presses / (self.num_chars + 1))
            print("presses per word: ", self.num_presses / (self.num_words + 1))
            print("error rate: ", self.num_errors / (self.num_selections + 1) * 100)
            print("fp rate: ", self.num_fp / self.time.time())

            self.update_sim_averages(trials)

            self.num_selections = 0
            self.num_chars = 0
            self.num_words = 0
            self.num_presses = 0
            self.num_errors = 0
            self.kde_errors = []

        self.save_simulation_data(attribute=attribute)

    def update_sim_averages(self, num_trials):

        time_int = self.time.time() - self.prev_time
        self.prev_time = float(self.time.time())

        self.sel_per_min += [self.num_selections / (time_int / 60)]

        self.char_per_min += [self.num_chars / (time_int / 60)]

        if self.num_selections > 0:
            self.press_per_sel += [self.num_presses / self.num_selections]

            self.error_rate_avg += [self.num_errors / self.num_selections]
        else:
            self.press_per_sel += [float("inf")]

            self.error_rate_avg += [float("inf")]

        if self.num_chars > 0:
            self.press_per_char += [self.num_presses / self.num_chars]
        else:
            self.press_per_char += [float("inf")]

        if self.num_words > 0:
            self.press_per_word += [self.num_presses / self.num_words]
        else:
            self.press_per_word += [float("inf")]

        if self.kde_errors_avg is None:
            self.kde_errors_avg = np.array(self.kde_errors) / num_trials
        else:
            length = min(len(self.kde_errors_avg), len(self.kde_errors))
            if len(self.kde_errors_avg) < len(self.kde_errors):
                self.kde_errors_avg += np.array(self.kde_errors[:length]) / num_trials
            else:
                self.kde_errors_avg = self.kde_errors_avg[:length] + np.array(self.kde_errors) / num_trials

    def type_text(self, text, verbose=False):
        self.target_text = text
        while len(self.target_text) > 0:
            target_clock, self.target_text = self.next_target(self.target_text)
            if verbose:
                print("Target: ", self.clock_to_text(target_clock), target_clock)

            recovery_time = 0.5
            self.time.set_time(self.time.time() + recovery_time)
            self.on_timer()

            self.select_clock(target_clock, verbose=verbose)

    def select_clock(self, target_clock, verbose=False, undo_depth=0):

        ndt = self.bc.clock_inf.clock_util.num_divs_time
        num_press = 0
        time_elapsed = 0
        for i in range(15):
            self.winner = False
            if self.bc.clock_inf.clock_util.cur_hours[target_clock] > ndt // 2:
                time_delta = (3 * ndt // 2 - self.bc.clock_inf.clock_util.cur_hours[
                    target_clock] + 1) / ndt * self.time_rotate
            else:
                time_delta = (ndt // 2 - self.bc.clock_inf.clock_util.cur_hours[target_clock] + 1) / ndt * self.time_rotate

            click_offset = np.float(np.random.choice(80, 1, p=self.click_dist) / 80.0 - 0.5) * config.period_li[config.default_rotate_ind]
            time_delta += click_offset
            time_elapsed += time_delta
            self.time.set_time(self.time.time() + time_delta)
            self.on_timer()
            self.on_press()
            num_press += 1
            if self.winner:

                self.num_chars += len(self.winner_text)
                if len(self.bc.clock_inf.win_history) > 1:
                    selected_clock = self.bc.clock_inf.win_history[1]
                else:
                    selected_clock = self.bc.clock_inf.win_history[0]
                if verbose:
                    print(">>> Clock " + str(selected_clock) + " selected in " + str(num_press) + " presses, " + str(round(time_elapsed, 2)) + " seconds")
                    print("    Typed \"" + self.winner_text + "\"")
                self.winner = False

                if selected_clock != target_clock:
                    self.num_errors += 1

                    print("Wrong clock, backtracking . . . ")
                    # undo_clock = self.keys_li.index(kconfig.mybad_char)*4 + 3
                    # if undo_depth < 3:
                    #     self.select_clock(undo_clock, undo_depth=undo_depth+1)
                    #     if target_clock != undo_clock:
                    #         self.select_clock(target_clock, verbose=False)
                else:
                    self.num_selections += 1

                break

            reaction_time = 0.3
            self.time.set_time(self.time.time() + reaction_time)
            time_elapsed += reaction_time
            self.on_timer()

        self.kde_errors += [self.kde_mse()]*num_press

    def next_target(self, text):
        words = text.split(" ")
        if "" in words:
            words.remove("")

        if len(words) > 1:
            remaining_words = ""
            for word in words[1:]:
                if remaining_words != "":
                    remaining_words += " "
                remaining_words += word
            first_word = words[0]
        else:
            remaining_words = ""
            first_word = words[0]

        target_word = self.context + first_word + " "
        if target_word in self.word_list:
            words_list_flattened = [word for sublist in self.words_li for word in sublist+[""]]
            return words_list_flattened.index(target_word), remaining_words

        target_letter = text[0]
        return self.keys_li.index(target_letter)*(self.N_pred+1) + self.N_pred, text[1:]

    def clock_to_text(self, index):

        if (index - self.N_pred) % (self.N_pred + 1) == 0:
            typed = self.keys_li[self.index_to_wk[index]]
        else:
            key = self.index_to_wk[index] // self.N_pred
            pred = self.index_to_wk[index] % self.N_pred
            typed = self.words_li[key][pred]
        return typed

    def gen_false_positive(self, return_time):
        self.num_fp += 1
        self.on_timer()
        self.on_press()
        self.time.set_time(return_time)
        self.on_timer()

    def plot_hist(self):
        bars = self.bc.get_histogram()
        bars = np.array(bars)/np.sum(bars)
        self.plot.plot_hist(bars)

    def kde_mse(self):
        bars = self.bc.get_histogram()
        bars = np.array(bars) / np.sum(bars)
        return np.sum(np.square(bars - self.click_dist))

    def init_locs(self):
        # size of keyboard
        self.N_rows = len(self.key_chars)
        self.N_keys_row = []
        self.N_keys = 0
        self.N_alpha_keys = 0
        for row in range(0, self.N_rows):
            n_keys = len(self.key_chars[row])
            for col in range(0, n_keys):
                if not isinstance(self.key_chars[row][col], list):
                    if self.key_chars[row][col].isalpha() and (len(self.key_chars[row][col]) == 1):
                        self.N_alpha_keys = self.N_alpha_keys + 1
                    elif self.key_chars[row][col] == kconfig.space_char and (len(self.key_chars[row][col]) == 1):
                        self.N_alpha_keys = self.N_alpha_keys + 1
                    elif self.key_chars[row][col] == kconfig.break_chars[1] and (
                            len(self.key_chars[row][col]) == 1):
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
        # self.N_pred = 2 # number of words per key
        self.key_height = 6.5 * kconfig.clock_rad
        self.w_canvas = 0
        self.index_to_wk = []  # overall index to word or key index
        for row in range(0, self.N_rows):
            y = row * self.key_height
            self.w_canvas = max(self.w_canvas, self.N_keys_row[row] * (6 * kconfig.clock_rad + kconfig.word_w))
            for col in range(0, self.N_keys_row[row]):
                x = col * (6 * kconfig.clock_rad + kconfig.word_w)
                # predictive words
                for word_index in range(self.N_pred):
                    self.clock_centers.append([x + word_clock_offset, y + (1 + word_index * 2) * kconfig.clock_rad])
                    self.word_locs.append([x + word_offset, y + (1 + word_index * 2) * kconfig.clock_rad])
                    # self.clock_centers.append([x + word_clock_offset, y + 3 * kconfig.clock_rad])
                    # self.clock_centers.append([x + word_clock_offset, y + 5 * kconfig.clock_rad])
                    self.index_to_wk.append(word + word_index)
                # win diffs
                self.win_diffs.extend([self.win_diff_base for i in range(self.N_pred)])
                # word position
                # self.word_locs.append([x + word_offset, y + 1 * kconfig.clock_rad])
                # self.word_locs.append([x + word_offset, y + 3 * kconfig.clock_rad])
                # self.word_locs.append([x + word_offset, y + 5 * kconfig.clock_rad])
                # rectangles
                self.rect_locs.append([x + rect_offset, y, x + rect_end, y + 2 * kconfig.clock_rad])
                self.rect_locs.append(
                    [x + rect_offset, y + 2 * kconfig.clock_rad, x + rect_end, y + 4 * kconfig.clock_rad])
                self.rect_locs.append(
                    [x + rect_offset, y + 4 * kconfig.clock_rad, x + rect_end, y + 6 * kconfig.clock_rad])
                # indices

                # self.index_to_wk.append(word)
                # self.index_to_wk.append(word + 1)
                # self.index_to_wk.append(word + 2)
                index += self.N_pred
                word += self.N_pred

                ## key character
                # reference to index of key character
                key_char = self.key_chars[row][col]
                self.keys_li.append(self.key_chars[row][col])
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
                    self.win_diffs.append(self.win_diff_base)
                index += 1
                key += 1

    def gen_scale(self):
        scale_length = self.w_canvas / 2  # (len(kconfig.key_chars[0])-1)*kconfig.word_w
        tick_int = int((len(config.period_li) - 1) * kconfig.word_pt * 3 / (1.0 * scale_length)) + 1
        self.time_rotate = config.period_li[self.rotate_index]

    def change_speed(self):
        self.bc.clock_inf.clock_util.change_period(self.time_rotate)


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
        # self.mainWidget.histogram.update()

    def init_words(self):
        if self.lm_left_context:
            lm_left_context = self.left_context
        else:
            lm_left_context = ""
        (self.words_li, self.word_freq_li, self.key_freq_li) = self.lm.get_words(lm_left_context, self.context,
                                                                                 self.keys_li)

        self.word_id = []
        self.word_pair = []
        word = 0
        index = 0
        windex = 0
        self.words_on = []
        self.words_off = []
        self.word_list = []
        # self.flag_args = []

        # if word prediction on but reduced
        if self.word_pred_on == 1:
            flat_freq_list = np.array([freq for sublist in self.word_freq_li for freq in sublist])
            if len(flat_freq_list) >= self.reduce_display:
                # replacement_count = 0
                for arg in flat_freq_list.argsort()[-self.reduce_display:]:
                    word_to_add = self.words_li[(arg // self.N_pred)][arg % self.N_pred]
                    # =============================================================================
                    #                     while len(word_to_add) == 1:
                    #                         replacement_count +=1
                    #                         new_arg = flat_freq_list.argsort()[-self.reduce_display-replacement_count]
                    #                         word_to_add = self.words_li[(new_arg /3)][new_arg%3]
                    # =============================================================================
                    if word_to_add != '':
                        if word_to_add not in self.word_list:
                            self.word_list.append(word_to_add)


            else:
                temp_word_list = [word_item for sublist in self.words_li for word_item in sublist]
                for word_item in temp_word_list:
                    if word_item != '':
                        self.word_list.append(word_item)


        # if word prediction completely on
        elif self.word_pred_on == 2:
            temp_word_list = [word_item for sublist in self.words_li for word_item in sublist]
            for word_item in temp_word_list:
                if word_item != '':
                    self.word_list.append(word_item)

            # print "TURNED ON AND WORD LIST IS" + str(self.word_list)

        len_con = len(self.context)
        for key in range(0, self.N_alpha_keys):
            for pred in range(0, self.N_pred):
                word_str = self.words_li[key][pred]
                len_word = len(word_str)
                if (len_con > 1) and (len_word > kconfig.max_chars_display):
                    word_str = "+" + word_str[len_con:len_word]
                self.word_pair.append((key, pred))
                if word_str == '':
                    self.words_off.append(index)
                else:
                    # turn word prediciton off
                    if self.word_pred_on == 0:
                        self.words_off.append(index)
                    # word prediction completely on
                    elif self.word_pred_on == 2:
                        self.words_on.append(index)
                    # word prediction turned on but reduced
                    # rank words frequency and display only three
                    else:
                        if windex in flat_freq_list.argsort()[-self.reduce_display:]:
                            self.words_on.append(index)
                        else:
                            self.words_off.append(index)

                windex += 1
                word += 1
                index += 1
            self.words_on.append(index)
            self.word_pair.append((key,))
            index += 1
        for key in range(self.N_alpha_keys, self.N_keys):
            for pred in range(0, self.N_pred):
                word_str = self.words_li[key][pred]
                self.word_pair.append((key, pred))
                self.words_off.append(index)
                index += 1
            self.words_on.append(index)
            self.word_pair.append((key,))
            index += 1
        self.typed_versions = ['']

    def draw_words(self):
        if self.lm_left_context:
            lm_left_context = self.left_context
        else:
            lm_left_context = ""
        (self.words_li, self.word_freq_li, self.key_freq_li) = self.lm.get_words(lm_left_context, self.context,
                                                                                 self.keys_li)
        word = 0
        index = 0
        self.words_on = []
        self.words_off = []
        self.word_list = []

        # if word prediction on but reduced
        if self.word_pred_on == 1:
            flat_freq_list = np.array([np.exp(freq) for sublist in self.word_freq_li for freq in sublist])
            if len(flat_freq_list) >= self.reduce_display:
                for arg in flat_freq_list.argsort()[-self.reduce_display:]:
                    word_to_add = self.words_li[(arg // 3)][arg % 3]
                    if word_to_add != '':
                        self.word_list.append(word_to_add)
            else:
                temp_word_list = [word_item for sublist in self.words_li for word_item in sublist]
                for word_item in temp_word_list:
                    if word_item != '':
                        self.word_list.append(word_item)
            self.word_list.reverse()
        # if word prediction completely on
        elif self.word_pred_on == 2:
            temp_word_list = [word_item for sublist in self.words_li for word_item in sublist]
            for word_item in temp_word_list:
                if word_item != '':
                    self.word_list.append(word_item)

        len_con = len(self.context)

        windex = 0
        for key in range(0, self.N_alpha_keys):
            for pred in range(0, self.N_pred):
                word_str = self.words_li[key][pred]
                len_word = len(word_str)
                if len_con > 1 and len_word > kconfig.max_chars_display:
                    word_str = "+" + word_str[len_con:len_word]
                if word_str == '':
                    self.words_off.append(index)
                else:
                    # turn word prediciton off
                    if self.word_pred_on == 0:
                        self.words_off.append(index)
                    # word prediction completely on
                    elif self.word_pred_on == 2:
                        self.words_on.append(index)
                    # word prediction turned on but reduced
                    # rank words frequency and display only three
                    else:
                        if windex in flat_freq_list.argsort()[-self.reduce_display:]:
                            self.words_on.append(index)
                        else:
                            self.words_off.append(index)

                windex += 1
                word += 1
                index += 1
            self.words_on.append(index)

            self.word_pair.append((key,))
            index += 1
        for key in range(self.N_alpha_keys, self.N_keys):
            for pred in range(0, self.N_pred):
                self.word_pair.append((key, pred))
                self.words_off.append(index)
                index += 1
            self.words_on.append(index)
            self.word_pair.append((key,))
            index += 1

        # self.mainWidget.update_clocks()
        # self.init_clocks()

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
                    if self.keys_li[key] in kconfig.break_chars:
                        prob = np.log(kconfig.break_prob)
                    if self.keys_li[key] == kconfig.back_char:
                        prob = np.log(kconfig.back_prob)
                    if self.keys_li[key] == kconfig.clear_char:
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
                        self.word_score_prior.append(0)
                else:
                    self.word_score_prior.append(0)

    def reset_context(self):
        self.left_context = ""
        self.context = ""
        self.typed = ""
        self.lm_prefix = ""
        self.draw_words()

    def draw_typed(self):
        self.wpm_update()
        redraw_words = False
        # phrases

        delete = False
        undo = False
        if self.phrase_prompts:
            previous_text = self.mainWidget.text_box.toPlainText().split("\n")[-1]
        else:
            previous_text = self.mainWidget.text_box.toPlainText()

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

        self.winner_text = new_text

        if new_text in  [". ",", ","? ", "! "]:
            previous_text = previous_text[:-1]
            redraw_words = True

        index = self.previous_winner
        if self.mainWidget.clocks[index] != '':
            if self.mainWidget.clocks[index].text in [kconfig.mybad_char, 'Undo']:
                undo = True
                delete = False
        if self.typed_versions[-1] == '' and len(self.typed_versions) > 1:
            undo_text = 'Clear'

        if self.clear_text:
            self.typed_versions += ['']
            self.mainWidget.text_box.setText('')
            self.clear_text = False
            undo_text = 'Clear'

        elif delete:
            # self.prefix = self.prefix[:-1]
            if self.typed_versions[-1] != '':
                self.typed_versions += [previous_text[:-1]]
                self.mainWidget.text_box.setText("<span style='color:#000000;'>" + self.typed_versions[-1] + "</span>")
        elif undo:
            if len(self.typed_versions) > 1:
                self.typed_versions = self.typed_versions[:-1]
                self.mainWidget.text_box.setText("<span style='color:#000000;'>" + self.typed_versions[-1] + "</span>")
        else:
            self.typed_versions += [previous_text + new_text]
            self.mainWidget.text_box.setText(
                "<span style='color:#000000;'>" + previous_text + "</span><span style='color:#00dd00;'>"
                + new_text + "</span>")

        if undo_text == kconfig.mybad_char:
            undo_text = "Undo"
        elif undo_text == kconfig.back_char:
            undo_text = "Backspace"
        elif undo_text == kconfig.clear_char:
            undo_text = "Clear"

        self.previous_undo_text = undo_text
        self.mainWidget.undo_label.setText("<font color='green'>" + undo_text + "</font>")

        if redraw_words:
            self.reset_context()

        if self.phrase_prompts:
            self.update_phrases(self.typed_versions[-1])

    def on_timer(self):
        self.bc.clock_inf.clock_util.increment(self.words_on)

    def on_press(self):
        self.num_presses += 1
        self.bc.select()

    def make_choice(self, index):
        is_undo = False
        is_equalize = False


        # highlight winner
        self.previous_winner = index
        # self.highlight_winner(index)

        # initialize talk string
        talk_string = ""

        # if selected a key
        if (index - self.N_pred) % (self.N_pred + 1) == 0:
            new_char = self.keys_li[self.index_to_wk[index]]
            # special characters
            if new_char == kconfig.space_char:
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
                # if delete the last character that turn
                self.old_context_li.append(self.context)
                # print(self.context)
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

            elif new_char.isalpha() or new_char == "'":
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
            key = self.index_to_wk[index] // self.N_pred
            pred = self.index_to_wk[index] % self.N_pred
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

        self.draw_words()
        # self.draw_typed()
        # update the word prior
        self.gen_word_prior(is_undo)

        # # talk the string
        # if self.talk_set.get() == 1:
        #     self.talk_winner(talk_string)

        # write output
        if self.is_write_data:
            self.params_handle_dict['choice'].append([time.time(), is_undo, is_equalize, self.typed])



        return self.words_on, self.words_off, self.word_score_prior, is_undo, is_equalize

    def save_simulation_data(self, attribute=None):
        data_file = os.path.join(self.data_loc, "npred_"+str(self.N_pred)+"_nwords_"+str(self.num_words_total)+"_lcon_"
                                 +str(int(self.lm_left_context))+"_wdiff_"+str(round(np.exp(self.win_diff_base)))
                                 +"_rot_"+str(self.rotate_index)+"_cor_"+str(self.easy_phrase)+"_fp_"
                                 +str(self.false_positive_rate)+".p")
        data_handel = PickleUtil(data_file)

        dist_id_file = os.path.join(self.data_loc, "dist_id.p")
        dist_id_handel = PickleUtil(dist_id_file)
        dist_id_handel.safe_save(self.click_dist)

        data_dict = dict()
        data_dict["N_pred"] = self.N_pred
        data_dict["prob_thresh"] = self.prob_thres
        data_dict["win_diff"] = self.win_diff_base
        data_dict["num_words"] = self.num_words_total
        data_dict["time_rotate"] = self.time_rotate
        data_dict["false_positive"] = self.false_positive_rate
        data_dict["errors"] = self.error_rate_avg
        data_dict["selections"] = self.sel_per_min
        data_dict["characters"] = self.char_per_min
        data_dict["presses_sel"] = self.press_per_sel
        data_dict["presses_char"] = self.press_per_char
        data_dict["presses_word"] = self.press_per_word
        data_dict["kde_mses"] = self.kde_errors_avg
        data_dict["kde"] = self.bc.get_histogram()
        data_dict["kde"] = self.bc.get_histogram()
        if attribute is not None:
            data_dict["attribute"] = attribute
        data_handel.safe_save(data_dict)

    def gen_data_dir(self):
        if self.job_num is not None:
            if not os.path.exists(os.path.join(self.working_dir, "sim_data")):
                try:
                    os.mkdir(os.path.join(self.working_dir, "sim_data"))
                except FileExistsError:
                    pass

            if not os.path.exists(os.path.join(os.path.join(self.working_dir, "sim_data"), str(self.job_num))):
                try:
                    os.mkdir(os.path.join(os.path.join(self.working_dir, "sim_data"), str(self.job_num)))
                except FileExistsError:
                    pass
            self.data_loc = os.path.join(os.path.join(self.working_dir, "sim_data"), str(self.job_num))
        else:
            dist_found = False
            highest_user_num = 0
            if not os.path.exists(os.path.join(self.working_dir, "sim_data")):
                try:
                    os.mkdir(os.path.join(self.working_dir, "sim_data"))
                except FileExistsError:
                    pass

            for path, dir, files in os.walk(os.path.join(self.working_dir, "sim_data")):
                highest_user_num = max(max([0]+[int(d) for d in dir]), highest_user_num)
                for file in files:
                    if "dist_id" in file:
                        file_handel = PickleUtil(os.path.join(path, file))
                        dist_id = file_handel.safe_load()
                        if np.sum(np.array(dist_id) - np.array(self.click_dist)) == 0:
                            dist_found = True
                            self.data_loc = path

            if not dist_found:
                try:
                    os.mkdir(os.path.join(os.path.join(self.working_dir, "sim_data"), str(highest_user_num+1)))
                except FileExistsError:
                    pass
                self.data_loc = os.path.join(os.path.join(self.working_dir, "sim_data"), str(highest_user_num+1))

    def closeEvent(self, event):
        print("CLOSING THRU CLOSEEVENT")
        self.quit(event)
        # self.deleteLater()

    def quit(self, event=None):
        self.bc.quit_bc()
        self.close()


def normal_hist(mu, sigma):
    n_bars = config.num_divs_click
    bars = (np.arange(n_bars) - n_bars//2)
    bars_over = (np.arange(n_bars) + n_bars//2)
    bars_under = (np.arange(n_bars) - n_bars*3//2)
    out = np.exp(-np.square(bars - mu) / (2 * sigma ** 2)) / np.sqrt(2 * np.pi * sigma ** 2)
    out += np.exp(-np.square(bars_over - mu) / (2 * sigma ** 2)) / np.sqrt(2 * np.pi * sigma ** 2)
    out += np.exp(-np.square(bars_under - mu) / (2 * sigma ** 2)) / np.sqrt(2 * np.pi * sigma ** 2)
    return out/np.sum(out)


class HistPlot():
    def __init__(self):
        self.plot_colors = ["#0000ff", "#00aa00", "#aa0000", "#ff7700", "#aa00aa"]
        self.color_num = 0

        self.fig = plt.figure()
        self.ax = plt.subplot(111)

    def plot_hist(self, bars):
        plot_color = self.plot_colors[self.color_num]
        self.color_num += 1

        bars = np.array(bars)

        mean = np.average(np.arange(len(bars)), weights=bars)
        std = np.sqrt(np.average((np.arange(len(bars)) - mean)**2, weights=bars))
        plt.bar(np.arange(len(bars)), bars, color=plot_color, alpha=0.3)

        plt.axvline(mean, color=plot_color, linestyle="--", alpha=0.8)
        for i in [-1, 1]:
            plt.axvline(mean + i * std, color=plot_color, linestyle=":", alpha=0.6)

    def show(self):
        self.ax.legend()
        plt.show()


def main():

    # hp = HistPlot()
    #
    kde = PickleUtil("C:\\Users\\nickb\\AppData\\Local\\Nomon\\data\\999\\user_histogram.p").safe_load()
    click_dist = kde(np.arange(80))
    click_dist /= np.sum(click_dist)

    # parameters_list = [{"click_dist": normal_hist(0, i/2)} for i in range(1,20)]
    # attributes = [i/2 for i in range(1,20)]
    # for parameters, attribute in zip(parameters_list, attributes):
    sim = SimulatedUser()
    params = {"N_pred": 3, "num_words": 17, "time_rotate": config.default_rotate_ind, "click_dist": click_dist}

    sim.parameter_metrics(params, num_clicks=500, trials=1)

    # sim = SimulatedUser()
    # params = {"N_pred": 3, "num_words": 17, "win_diff": np.log(99), "click_dist": click_dist}
    #
    # sim.parameter_metrics(params, num_clicks=500, trials=1)


if __name__ == "__main__":
    main()
