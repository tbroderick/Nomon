#!/usr/bin/env python2

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
        self.get_all_data()

        if self.parent.is_simulation:
            self.latest_time = self.parent.time.time()
            self.last_press_time = self.parent.time.time()
        else:
            self.latest_time = time.time()
            self.last_press_time = time.time()
        self.last_gap_time_li = []
        self.last_press_time_li = []
        
        #NOT SUPER SURE
        self.time_rotate = self.parent.time_rotate
    
    def get_histogram(self):
        return self.clock_inf.kde.dens_li
    
    def get_all_data(self):
        self.get_click_data()
        self.get_prev_data()

    #get kde data from past use
    def get_prev_data(self):
        if self.parent.is_write_data:
            self.prev_data_path = self.parent.data_handel + "\\preconfig.p"
            print("USER ID is" + str(self.parent.user_id))
            load_dict = PickleUtil(self.prev_data_path).safe_load()
            if load_dict != None:
                self.clock_inf.kde.get_past_dens_li(load_dict)
    
    def get_click_data(self):

        if self.parent.is_write_data:
            self.click_data_path = self.parent.data_handel + "\\click_time_log_" + str(self.parent.use_num-1)+".p"

            load_click = PickleUtil(self.click_data_path).safe_load()
            self.click_time_list = []
            if load_click != None:
                try:
                    if load_click.has_key('user id') and load_click.has_key('use_num') and load_click.has_key('rotate index'):
                        if load_click['user id'] == self.parent.user_id:
                            self.click_time_list = load_click['click time list']
                            # self.parent.use_num = load_click['use_num'] +1
                            self.parent.rotate_index = load_click['rotate index']
                            return
                except:
                    pass

            self.parent.rotate_index = config.default_rotate_ind
            return

    def save_click_time(self, last_press_time, last_gap_time, index):

        self.parent.params_handle_dict['press'].append([last_press_time])
        self.click_time_list.append((last_gap_time, index))
      
    def save_when_quit_noconsent(self):
        if self.parent.is_write_data:
            PickleUtil(self.click_data_path).safe_save({'user id': self.parent.user_id, 'use_num': self.parent.use_num ,'click time list': [], 'rotate index': self.parent.rotate_index})

    #ALL THE SAVES AND DUMPS THEY DO WHEN THEY QUIT KEYBOARD SHOULD BE HERE TOO
    def save_when_quit(self):
            user_preferences = self.parent.clock_type, self.parent.font_scale, self.parent.high_contrast, \
                               self.parent.layout_preference, self.parent.pf_preference, self.parent.rotate_index, \
                               self.parent.is_write_data
            self.parent.up_handel.safe_save(user_preferences)


            self.prev_data_path = os.path.join(self.parent.data_handel, 'preconfig.p')
            self.click_data_path = os.path.join(self.parent.data_handel, 'click_time_log_' + str(self.parent.use_num)+'.p')
            self.params_data_path = os.path.join(self.parent.data_handel, 'params_data_use_num' + str(self.parent.use_num)+'.p')
            print(self.params_data_path)
            PickleUtil(self.click_data_path).safe_save({'user id': self.parent.user_id, 'use_num': self.parent.use_num ,'click time list': self.click_time_list, 'rotate index': self.parent.rotate_index})
            PickleUtil(self.prev_data_path).safe_save({'li': self.clock_inf.kde.dens_li, 'z': self.clock_inf.kde.Z, 'opt_sig': self.clock_inf.kde.ksigma, 'y_li': self.clock_inf.kde.y_li, 'yksigma':self.clock_inf.kde.y_ksigma})
            PickleUtil(self.params_data_path).safe_save(self.parent.params_handle_dict)

    def quit_bc(self):

        if self.parent.is_write_data:
            self.save_when_quit()
        else:
            self.save_when_quit_noconsent()

    def select(self):
        ####CLOCKUTIL에서 달라진 INCREMTNT, 달라진 KDE, 달라진 SCOREFUNCTION 갖다 바꾸기
        if self.parent.is_simulation:
            time_in = self.parent.time.time()
        else:
            time_in = time.time()
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
        last_gap_time = (time_in - self.last_press_time) % self.time_rotate
        if self.parent.is_write_data:
            self.last_press_time = time_in
            self.last_gap_time_li += [last_gap_time]  # save time of click % rotate index
            self.last_press_time_li += [time_in]
            # print "click time was recorded!"

        # proceed based on whether there was a winner
        if (self.clock_inf.is_winner()):
            if self.parent.is_simulation:
                self.parent.winner = True
                self.parent.winner_text = self.parent.clock_to_text(self.clock_inf.sorted_inds[0])
                # print("WINNER",  self.clock_inf.sorted_inds[0])

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
        if self.parent.is_simulation:
            self.start_time = self.parent.time.time()
        else:
            self.start_time = time.time()

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

        if not self.parent.is_simulation:
            for clock_index in self.clock_inf.clocks_on:
                clock = self.parent.mainWidget.clockgrid_widget.clocks[clock_index]

                if clock is not None:
                    if self.clock_inf.cscores[clock_index] > bound_score:
                        clock.highlighted = True
                    else:
                        clock.highlighted = False
