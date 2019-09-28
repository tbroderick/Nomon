#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 15:28:48 2018
@author: TiffMin
"""
from __future__ import division
import numpy as np
from clock_util import ClockUtil
import config


def log_normalize(dist):
    dist = np.array(dist)
    log_sum = -float("inf")
    for i in dist:
        log_sum = np.logaddexp(log_sum, i)
    return dist - log_sum


class Entropy:
    
    def __init__(self, clock_inf):
        self.clock_inf = clock_inf
        self.num_bits = 0
        self.bits_per_select = np.log(len(self.clock_inf.clocks_on)) / np.log(2)

    def update_bits(self):
        K = len(self.clock_inf.clocks_on)
        self.bits_per_select = np.log(K) / np.log(2)
        self.num_bits += self.bits_per_select
        return self.num_bits


class KernelDensityEstimation:
    
    def __init__(self, time_rotate, past_data=None):
        self.dens_li = []
        self.Z = 0
        self.ksigma =0
        self.ksigma0 = 0
        self.y_li = []
        self.y_ksigma = []
        self.damp = 0.96
        self.n_ksigma = max(5, int(1.0 / (1 - self.damp)))
        self.ns_factor = 1.06 / (self.n_ksigma ** 0.2)
        self.time_rotate = time_rotate

        # histogram bin index
        self.index_li = range(0, config.num_divs_click)
        # location of the histogram bins
        self.x_li = [index * self.time_rotate / config.num_divs_click - self.time_rotate / 2.0 \
                     for index in self.index_li]
        
        self.past_data = past_data 
        self.initialize_dens()
    
    def initialize_dens(self):
        self.Z = 0
        self.dens_li = []
        for x in self.x_li:
            diff = x - config.mu0

            dens = np.exp(-1/(2*config.sigma0_sq) * diff*diff)
            dens /= np.sqrt(2*np.pi*config.sigma0_sq)
            dens *= self.n_ksigma
            self.dens_li.append(dens)
            self.Z += dens
        self.ksigma0 = 1.06*config.sigma0 / (self.n_ksigma**0.2)
        self.ksigma = self.ksigma0
    
    # Assumes that data is a dictionary
    # of key z, dens ..
    def get_past_dens_li(self, dens_dict):
        if 'li' in dens_dict and 'z' in dens_dict and 'opt_sig' in dens_dict and 'y_li' in dens_dict:
            print("HAS KEY THO")

            self.dens_li = dens_dict['li']
            print("I'm starting(reading) and the self.dens_li" + str(dens_dict['li']))
            self.Z =  dens_dict['z']
            self.ksigma = dens_dict['opt_sig']
            print("Also the self.ksimga0" + str(dens_dict['opt_sig']))
            # THIS LINE ?????????
            # self.y_li_from_pre = dens_dict['y_li']
            self.y_li = dens_dict['y_li']
            self.y_ksigma = dens_dict['yksigma']
            print("IS THIS LINE THE PROBLEM?")
    
    # helper functions
    def normal(self, x, mu, sig_sq):
        return np.exp(-((x-mu)**2)/(2*sig_sq)) / float(np.sqrt(2*np.pi*sig_sq))
    
    def optimal_bandwith(self, things):
        n = len(things)
        return 1.06 * (n ** -0.2) * np.std(things)

    def ave_sigma_sq(self, eff_num_points, yLenEff):
        ysum = sum([y for y in self.y_li[0:yLenEff]])
        y2sum = sum([y**2 for y in self.y_li[0:yLenEff]])
        ave_sigma_sq = (self.n_ksigma - yLenEff) * self.ksigma0 * self.ksigma0
        if (yLenEff > 0):
            ave_sigma_sq += y2sum - ysum * ysum / yLenEff
        ave_sigma_sq /= self.n_ksigma
        
        return ave_sigma_sq

    # calculate the optimal bandwidth only with the latest yLenEff(effective) data
    def calc_ksigma(self, eff_num_points, yLenEff):
        # combine emnp.pirical and prior
        ave_sigma_sq = self.ave_sigma_sq(eff_num_points, yLenEff)

        # optimal bandwidth
        self.ksigma = self.ns_factor * np.sqrt(max(0.0001, ave_sigma_sq))
        return self.ksigma

    # When a new yin comes in, add that yin to kernel density estimation
    def increment_dens(self, yin, ksigma):
        self.Z = 0
        ksigma_sq = ksigma * ksigma
        for index in self.index_li:
            diff = self.x_li[index] - yin
            dens = np.exp(-1 / (2 * ksigma_sq) * diff * diff)
            dens /= np.sqrt(2 * np.pi * ksigma_sq)
            self.dens_li[index] = self.damp * self.dens_li[index] + dens
            # summing Z again to keep it fresh (& since have to anyway)
            self.Z += self.dens_li[index]
            

class ClockInference:
    
    def __init__(self, parent, bc, past_data=None, fast_select=False):
        self.parent = parent
        self.bc = bc
        self.fast_select = fast_select
        self.clock_util = ClockUtil(self.parent, self.bc, self)


        # if not self.fast_select:
        self.clocks_li = range(0, len(self.parent.clock_centers))

        self.clocks_on = self.parent.words_on

        self.press_cscores = []
        self.cscores = [0] * len(self.parent.clock_centers)
        # else:
        #     self.clocks_li = range(0, 4)
        #
        #     self.clocks_on = list(range(4))
        #
        #     self.press_cscores = []
        #     self.cscores = [0] * 4

        self.clock_locs = []
        self.prev_cscores = list(self.cscores)
        # NOT SUPER SURE - > OKAY TO BE SURE. DONE IN KEYBOARD RIGHT NOW
        self.clock_history = [[]]
        
        # deep copy clocks_on
        self.sorted_inds = list(self.clocks_on)
        self.win_diffs = self.parent.win_diffs
        
    
        # NOT SUPER SURE
        self.time_rotate = self.parent.time_rotate

        self.entropy = Entropy(self)
        self.kde = KernelDensityEstimation(self.time_rotate)
        
        # how many pts to save (0.02: threshold for accuracy)
        self.n_hist = min(200, int(np.log(0.02) / np.log(self.kde.damp)))
        
        self.past_data = past_data

    # Load past data if there is such
    def load_kde(self):
        if self.past_data is not None:
            pass

    # return the click score for a particular press time
    def get_score_inc(self, yin):
        index = int(config.num_divs_click * (yin / self.time_rotate + 0.5)) % config.num_divs_click
        if self.kde.Z != 0: 
            return np.log(self.kde.dens_li[index] / self.kde.Z)
        # Not super sure tho
        else:
            return 1

    def reverse_index_gsi(self, log_dens_val):
        dens_val = np.e ** log_dens_val
        most_likely_index = np.argmin([abs(x - dens_val) for x in self.kde.dens_li])
        return most_likely_index
    
    # increments and adds the new x to the ksigma calculation
    def inc_score_inc(self, yin):
        # add to the list
        if self.bc.parent.is_write_data:
            ind_in_histo = np.argmin(np.abs(np.array(self.kde.x_li)-yin))  # save relative click time
            self.bc.save_click_time(self.bc.last_press_time_li.pop(0), self.bc.last_gap_time_li.pop(0), ind_in_histo)
            print("Click Time Recorded!")

        if len(self.kde.y_li) > self.n_hist:
            self.kde.y_li.pop()
            self.kde.y_ksigma.pop()
        self.kde.y_li.insert(0, yin)
        self.kde.y_ksigma.insert(0, self.kde.ksigma)
        # calculations
        self.kde.increment_dens(yin, self.kde.ksigma)
        self.kde.calc_ksigma(self.n_hist, min(self.kde.n_ksigma, len(self.kde.y_li)))

    def update_scores(self, time_diff_in):
        clock_locs = [0] * len(self.cscores)
        for clock in self.clocks_on:
            time_in = self.clock_util.cur_hours[
                          clock] * self.time_rotate * 1.0 / self.clock_util.num_divs_time + time_diff_in - self.time_rotate * config.frac_period

            self.cscores[clock] = self.get_score_inc(time_in)
            clock_locs[clock] = time_in

        self.press_cscores += [self.cscores.copy()]
        self.clock_locs += [clock_locs]
        self.update_sorted_inds()

    def update_dens(self, new_time_rotate):
        # reset period
        self.time_rotate = new_time_rotate
        # location of histogram bins
        self.kde.x_li = []
        for index in self.kde.index_li:
            self.kde.x_li.append(index * self.time_rotate / config.num_divs_click - self.time_rotate / 2.0)
        for n in range(0, len(self.kde.y_li)):
            self.kde.increment_dens(self.kde.y_li[n], self.kde.y_ksigma[n])
        # min(self.n_ksigma, len(self.y_li)) is the effective number of recent y_li
        self.kde.calc_ksigma(self.n_hist, min(self.kde.n_ksigma, len(self.kde.y_li)))

    # update clock history
    def update_history(self, time_diff_in):
        # number of presses so far up to now
        self.clock_history[0].append([])
        # rewrote the original code to make it more clear
        clocks_on_cursor = 0
        for i in range(len(self.clocks_li)):
            if i == self.clocks_on[clocks_on_cursor]:
                # mod and 0.5's for keeping in (-0.5,0.5) range
                click_time = (self.clock_util.cur_hours[i] * self.time_rotate * 1.0 / self.clock_util.num_divs_time +
                              time_diff_in - self.time_rotate * config.frac_period + 0.5) % 1 - 0.5

                self.clock_history[0][-1].append(click_time)
                clocks_on_cursor += 1
            else:
                self.clock_history[0][-1].append(0)
    
    def compare_score(self, index):
        return -self.cscores[index]

    def update_sorted_inds(self):
        self.sorted_inds = list(self.clocks_on)
        self.sorted_inds.sort(key=self.compare_score)

    # Determines if there exists a winner at the current moment
    def is_winner(self):

        # if len(self.press_cscores) > 0:
        #     prod_c_scores = np.sum(self.press_cscores, axis=0)
        #     prod_c_scores = log_normalize(prod_c_scores)
        #
        #     argmax_pc_score = np.argmax(prod_c_scores)
        #     max_pc_score = prod_c_scores[argmax_pc_score]
        #
        #     prod_c_scores[argmax_pc_score] = -float("inf")
        #     max_pc_score_2 = np.max(prod_c_scores)
        #
        #     print("AAA", max_pc_score - max_pc_score_2)
        #     if max_pc_score - max_pc_score_2 > config.win_diff_base:
        #         print("WINNER: ")

        if self.bc.word_press_index >= 1:
            space_index = self.parent.keys_li.index(" ")

            scores = np.sum(self.press_cscores[-1:], axis=0)

            log_prob_sum = -float("inf")
            for log_prob in scores:
                log_prob_sum = np.logaddexp(log_prob_sum, log_prob)
            scores -= log_prob_sum

            space_prob = scores[space_index]

            # print(space_prob)
            if space_prob > -2:
                return True
        return False

    # win_history -> GUESS FINE
        
    def learn_scores(self, is_undo):
        n_hist = len(self.clock_history)
        if is_undo:
            # if just undid, delete the latest histories (history for this "undo" press and one before); 0:2 == [0,1]
            if (n_hist > 1):
                del self.clock_history[0:2]
                del self.win_history[0:2]
            else:
                self.clock_history = []
                self.win_history = []
            
        elif n_hist > config.learn_delay:
            # index of the winning clock

            num_selections = len(self.clock_history)
            # add a score point to the location of each recorded press
            # for selection_index in range(num_selections-1, -1, -1):
            selection_index = -config.learn_delay
            n_press = len(self.clock_history[selection_index])
            win_index = self.win_history[selection_index]
            for press in range(0, n_press):
                self.inc_score_inc(self.clock_history[selection_index][press][win_index])

            # delete extra bits
            # self.clock_history = []
            # self.win_history = []
            for index in range(n_hist - 1, config.learn_delay - 1, -1):
                self.clock_history.pop(index)
                self.win_history.pop(index)
        
        self.clock_history.insert(0, [])
        self.win_history.insert(0, -1)

    def handicap_cscores(self, is_win, is_start):
        if is_win or is_start:
            # handicap the highest scorer if it would be "inevitable" otherwise
            if len(self.clocks_on) <= 1:
                pass
            elif self.cscores[self.sorted_inds[0]] - self.cscores[self.sorted_inds[1]] > config.max_init_diff:
                self.cscores[self.sorted_inds[0]] = self.cscores[self.sorted_inds[1]] + config.max_init_diff
