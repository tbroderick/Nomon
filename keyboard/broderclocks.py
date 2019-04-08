#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 16:00:14 2018
@author: TiffMin
"""
from __future__ import division
from clock_inference_engine import *
import time
import os
from numpy import log

from pickle_util import PickleUtil
import config


class BroderClocks:
    def __init__(self, parent):
        self.parent = parent
        self.parent.bc_init = True
        self.clock_inf = ClockInference(self.parent, self)
        
        self.is_undo = False
        self.is_equalize = False
        self.is_win = self.clock_inf.is_winner()
        self.is_start = False
                

        #SPECIFIC FILE NAMES
        #SAVING AND LOADING
    
        self.latest_time = self.parent.time.time()
        self.last_press_time = self.parent.time.time()
        self.last_gap_time_li = []
        self.last_press_time_li = []
        
        #NOT SUPER SURE
        self.time_rotate = self.parent.time_rotate
    
    def get_histogram(self):
        return self.clock_inf.kde.dens_li

    def quit_bc(self):

        if self.parent.is_write_data:
            self.save_when_quit()
        else:
            self.save_when_quit_noconsent()

    def select(self):
        ####CLOCKUTIL에서 달라진 INCREMTNT, 달라진 KDE, 달라진 SCOREFUNCTION 갖다 바꾸기
        time_in = self.parent.time.time()
        # update scores of each clock
        self.clock_inf.update_scores(time_in - self.latest_time)
        # update history of key presses
        if config.is_learning:
            self.clock_inf.update_history(time_in - self.latest_time)
        
        #Save selected time into file
        top_score_clock = self.clock_inf.sorted_inds[0]
        #그냥 curhour하면 되는거 아닌가 
        ind_in_histo = self.clock_inf.reverse_index_gsi(self.clock_inf.cscores[top_score_clock])

        #Save all click time by the user

        # proceed based on whether there was a winner
        if (self.clock_inf.is_winner()):
            print("WINNER",  self.clock_inf.sorted_inds[0])
            # record winner
            self.clock_inf.win_history[0] = self.clock_inf.sorted_inds[0]
            # update number of bits recorded
            self.clock_inf.entropy.update_bits()
            # call parent program with choice
            #일단은 넘어가지면 NEED TO MAKE WORDPRIOR HERE
            (self.clock_inf.clocks_on, self.clock_inf.clocks_off, clock_score_prior, self.is_undo,
             self.is_equalize) = self.parent.make_choice(self.clock_inf.sorted_inds[0])
            # learn new scores
            if config.is_learning:
                self.clock_inf.learn_scores(self.is_undo)
            self.parent.draw_histogram()
            # reset time indices
            self.init_round(True, False, clock_score_prior)
        else:
            # update time indices
            self.init_round(False, False, [])

         
    #CAN DO BETTER FOR THIS PART
    def init_bits(self):
        self.bits_per_select = log(len(self.clock_inf.clocks_on)) / log(2)
        self.start_time = self.parent.time.time()
        self.last_win_time = self.start_time
        self.num_bits = 0
        self.num_selects = 0
            
    def init_follow_up(self, clock_score_prior):
        # initialize
        self.init_round(False, True, clock_score_prior)
        ## history of click times
        self.clock_inf.clock_history = [[]]
        self.clock_inf.win_history = [-1]
        # whether the previous move was an "undo"
        self.just_undid = False
        ## bit rate initialize
        self.init_bits()
        
    def init_round(self, is_win, is_start, clock_score_prior):
        self.clock_inf.clock_util.init_round(self.clock_inf.clocks_li)
        self.clock_inf.clock_util.init_round(self.clock_inf.clocks_on)
        if (is_win or is_start):  # if won, restart everything
            if (is_win):
                # identify the undo button as the winner to highlight
                win_clock = self.clock_inf.sorted_inds[0]

            if (self.is_undo) and (not self.is_equalize):
                count = 0
                for clock in self.clock_inf.clocks_on:
                    self.clock_inf.cscores[clock] = 0
                    count += 1
                top_score = 0
            else:
                count = 0
                for clock in self.clock_inf.clocks_on:
                    self.clock_inf.cscores[clock] = clock_score_prior[count]
                    count += 1
                top_score = 0
        

        # update the sorted loading_text
        self.clock_inf.update_sorted_inds()
        #WHY IS THIS HERE?????
        self.clock_inf.clock_util.update_curhours(self.clock_inf.sorted_inds)

        self.clock_inf.handicap_cscores(is_win, is_start)
        top_score = self.clock_inf.cscores[self.clock_inf.sorted_inds[0]]
        # highlight all clockfaces "near" the winning score
        bound_score = top_score - self.parent.win_diffs[self.clock_inf.sorted_inds[0]]


       