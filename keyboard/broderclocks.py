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
from __future__ import division
import Tkinter
import config
import numpy
import time
import math
import random
import os
import pickle


# pre-compute locations of the hour hands for a given
# number of "hours" and a given radius
class HourLocs:
    def __init__(self, num_divs_time, radius):

        self.num_divs_time = num_divs_time  # amount of time filling and emptying
        self.radius = radius

        self.hour_locs = []
        self.hl_base = []
        for index in range(0, num_divs_time):
            base = - numpy.pi / 2.0 + (2.0 * numpy.pi * index) / num_divs_time
            theta = -config.theta0 + base
            self.hour_locs.append([self.radius * numpy.cos(theta), self.radius * numpy.sin(theta)])
            self.hl_base.append(base)

    # EXP: for experimenting
    def set(self, theta):
        for index in range(0, self.num_divs_time):
            base = self.hl_base[index]
            self.hour_locs[index] = [self.radius * numpy.cos(-theta + base), self.radius * numpy.sin(-theta + base)]


# specifies a prior on scores at the hour hand positions
# and gives a place where new scores can be stored as they
# are computed online
class HourScoreIncs:
    def __init__(self, use_num, user_id, time_rotate, prev_data):
        self.pressed_at_least_once = 0
        # rotation period
        self.time_rotate = time_rotate
        # index over histogram bins
        self.index_li = range(0, config.num_divs_click)
        # location of histogram bins
        self.x_li = []
        for index in self.index_li:
            self.x_li.append(index * self.time_rotate / config.num_divs_click - self.time_rotate / 2.0)
        # damping rate
        self.damp = 0.96
        # how many pts to save (0.02: threshold for accuracy)
        self.n_hist = min(200, int(numpy.log(0.02) / numpy.log(self.damp)))
        # effective number of points: for kernel bandwidth calculation
        self.n_ksigma = max(5, int(1.0 / (1 - self.damp)))
        # normal scale factor
        self.ns_factor = 1.06 / (self.n_ksigma ** 0.2)
        # latest data points
        self.y_li = []
        self.y_ksigma = []
        self.not_read_pickle = 0
        
    
        ## initialize the density histogram
        if os.path.exists("data/preconfig.pickle") and self.not_read_pickle == 0:
            print "using the trained preconfig!"
            with open("data/preconfig.pickle", 'rb') as handle:
                temp_dens = pickle.load(handle)
                self.dens_li = temp_dens[0]
                print "I'm starting(reading) and the self.dens_li" + str(temp_dens[0])
                self.Z = temp_dens[1]
                self.ksigma0 = temp_dens[2]
                print "Also the self.ksimga0" + str(temp_dens[2])
                self.ksigma = self.ksigma0 
                self.y_li_from_pre = temp_dens[3]
            self.not_read_pickle = 1
        else:
            print "couldn't find the trained preconfig!"
            self.Z = 0
            self.dens_li = []
            for x in self.x_li:
                diff = x - config.mu0
                dens = numpy.exp(-1/(2*config.sigma0_sq) * diff*diff)
                dens /= numpy.sqrt(2*numpy.pi*config.sigma0_sq)
                dens *= self.n_ksigma
                self.dens_li.append(dens)
                self.Z += dens
            self.ksigma0 = 1.06*config.sigma0 / (self.n_ksigma**0.2)
            self.ksigma = self.ksigma0





        ## add in previous data, if any
        if (use_num > 0):  # case: already have click data
            ## get data components
            self.y_li = prev_data[0]
            self.y_ksigma = prev_data[1]

            ## convert old data to new densities and ksigma
            self.update_dens(self.time_rotate)

        # finish initializing things in both cases
        self.ksigma_sq = self.ksigma * self.ksigma

    def update_dens(self, new_time_rotate):
        # reset period
        self.time_rotate = new_time_rotate
        # location of histogram bins
        self.x_li = []
        for index in self.index_li:
            self.x_li.append(index * self.time_rotate / config.num_divs_click - self.time_rotate / 2.0)
        
        #not pressed at all
        if self.not_read_pickle ==0:
            print "not read pickle"
            
        if os.path.exists("data/preconfig.pickle"):
            print "preconfig exists"
            
        if os.path.exists("data/preconfig.pickle") and self.not_read_pickle ==0:
            print "not pressed once so update from training"
            #update self.dens_li and other things
            empirical = [self.index_into_compatible_with_xloc(self.yin_into_index(yin)) for yin in self.y_li_from_pre] 
            opt_sig = self.optimal_bandwith(empirical)
            self.dens_li = []
            self.Z = 0
            for x in self.x_li:
                x_loc = x
                dens = sum([self.normal(x_loc, self.index_into_compatible_with_xloc(self.yin_into_index(yin)), opt_sig**2) for yin in self.y_li_from_pre])
                #print "dens" + str(dens)
                self.dens_li.append(dens)
                self.Z += dens
                
            self.not_read_pickle = 1
        
        yL = len(self.y_li)
        for n in range(0, yL):
            self.increment_dens(self.y_li[n], self.y_ksigma[n])
        self.calc_ksigma()

    #Helper functions         
    def normal(self, x, mu, sig_sq):
        return numpy.exp(-((x-mu)**2)/(2*sig_sq)) / float(numpy.sqrt(2*numpy.pi*sig_sq))
    
    # return the click score for a particular press time
    #yin will be index!
    def yin_into_index(self, yin):
        #yin_into_index = yin
        index = int(config.num_divs_click * (yin/self.time_rotate+0.5)) % config.num_divs_click
        return index
    
    def index_into_compatible_with_xloc(self, index):
        x_compat = index * self.time_rotate/config.num_divs_click - self.time_rotate/2.0
        return x_compat
    
    def optimal_bandwith(self, things):
        n = len(things)
        return 1.06 * (n ** -0.2) * numpy.std(things)




    def increment_dens(self, yin, ksigma):
        self.Z = 0
        ksigma_sq = ksigma * ksigma
        for index in self.index_li:
            diff = self.x_li[index] - yin
            dens = numpy.exp(-1 / (2 * ksigma_sq) * diff * diff)
            dens /= numpy.sqrt(2 * numpy.pi * ksigma_sq)
            self.dens_li[index] = self.damp * self.dens_li[index] + dens
            # summing Z again to keep it fresh (& since have to anyway)
            self.Z += self.dens_li[index]

    # increments and adds the new x to the ksigma calculation
    def inc_score_inc(self, yin):
        # add to the list
        if (len(self.y_li) > self.n_hist):
            self.y_li.pop()
            self.y_ksigma.pop()
        self.y_li.insert(0, yin)
        self.y_ksigma.insert(0, self.ksigma)
        # calculations
        self.increment_dens(yin, self.ksigma)
        self.calc_ksigma()

    # calculate the optimal bandwidth from the latest data
    def calc_ksigma(self):
        # how much
        yLenEff = min(self.n_ksigma, len(self.y_li))

        ysum = 0
        y2sum = 0
        for n in range(0, yLenEff):
            y = self.y_li[n]
            ysum += y
            y2sum += y * y

        # combine empirical and prior
        ave_sigma_sq = (self.n_ksigma - yLenEff) * self.ksigma0 * self.ksigma0
        if (yLenEff > 0):
            # n * ( sy2 / n - (sy/n)^2 )
            ave_sigma_sq += y2sum - ysum * ysum / yLenEff
        ave_sigma_sq /= self.n_ksigma

        # print str(ysum) + " " + str(y2sum) + " " + str(ave_sigma_sq)

        # optimal bandwidth
        self.ksigma_sq = self.ns_factor * self.ns_factor * ave_sigma_sq
        self.ksigma = numpy.sqrt(self.ksigma_sq)

    # return the click score for a particular press time
    def get_score_inc(self, yin):
        index = int(config.num_divs_click * (yin / self.time_rotate + 0.5)) % config.num_divs_click
        return numpy.log(self.dens_li[index] / self.Z)

    # plot exp(the click scores) across press times
    def get_plot(self):
        # don't return x information
        # effectively normalizing x coordinates for display
        return self.dens_li

    # finish up and save the user information
    def quit(self):
        return [self.y_li, self.y_ksigma]


# an array where the smallest integers (with 0 in front) are arranged
# so as to be as far apart as possible within the array
class SpacedArray:
    def __init__(self, nels):
        self.rev_arr = []
        insert_pt = 0
        level = 0
        for index in range(0, nels):
            self.rev_arr.insert(insert_pt, index + 1)
            insert_pt += 2
            if (insert_pt > 2 * (2 ** level - 1)):
                insert_pt = 0
                level += 1
        self.rev_arr.insert(0, 0)

        self.arr = []
        for index in range(0, nels + 1):
            self.arr.append(0)
        for index in range(0, nels + 1):
            self.arr[self.rev_arr[index]] = index


class BroderClocks:
    # parent: the calling program
    # ---must have own function parent.make_choice(clock_index) and parent.present_choice()
    # canvas: the drawing canvas to which we add the clocks
    # centers: an array of the positions of the clock centers
    # ---each element is an [x,y] pair
    # radius: the size of the hourhand on the clocks
    # file_handle: for printing interesting things
    # clocks_on: clocks in use (initially, for the first round)
    # clocks_off: clocks not in use (initially, for the first round)
    # clock_score_prior: prior for the clock scores
    # circle_off_color: color for the clocks when they are not in use (to blend into the bg)
    def __init__(self, parent, centers, win_diffs, radius, file_handle, clocks_on, clocks_off, circle_off_color,
                 in_time, use_num, user_id, time_rotate, prev_data):
        ### process the inputs ###
        ## copy
        self.parent = parent
        self.parent.bc_init = True
        self.centers = centers
        self.win_diffs = win_diffs
        self.radius = radius
        self.file_handle = file_handle
        self.clocks_on = clocks_on
        self.clocks_off = clocks_off
        self.circle_off_color = circle_off_color
        self.time_rotate = time_rotate
        ## related quantities
        # number of clocks
        self.N_clocks = len(self.centers)
        # list of clock indices
        self.clock_li = range(0, self.N_clocks)
        # number of unique clock positions in the animation
        self.num_divs_time = int(numpy.ceil(time_rotate / config.ideal_wait_s))
        # reset wait_s so num_divs_time is integer
        self.wait_s = time_rotate / self.num_divs_time


        self.use_num, self.user_id, self.time_rotate, self.prev_data = use_num, user_id, time_rotate, prev_data
        self.last_press_time = 0
        
        #If user id is the same, load the click_time_list in the saved file
        #Otherwise load empty list
        #Variables to dump/save in click_time_log.pickle
        if os.path.exists("data/click_time_log" + str(user_id) + "." + str(use_num) + ".pickle"):
            with open("data/click_time_log" + str(user_id) + "." + str(use_num) + ".pickle", 'rb') as temp_handle:
                try:
                    temp_saved_list = pickle.load(temp_handle)
                    #saved user id is the 0th element
                    if temp_saved_list[0] == user_id:
                        self.click_time_list =temp_saved_list[1]
                except:
                    self.click_time_list = []
        else:    
            self.click_time_list = []
        self.rot_change_list = [(0,self.time_rotate)]    
        
        ### initialize ###
        # time
        self.latest_time = in_time
        ## hour hand positions
        # find coordinates
        self.hl = HourLocs(self.num_divs_time, self.radius)
        # current index to location of hour hands
        self.cur_hours = []
        # next time for hour hands to start
        for clock in self.clock_li:
            self.cur_hours.append(0)  # just filling array for now; initialized below
        ## local canvas drawing
        # self.init_canvas_clocks()
        ## scores
        self.hsi = HourScoreIncs(use_num, user_id, time_rotate, prev_data)
        # current scores for this round
        self.cscores = []  # just initializing here; real values later
        for clock in self.clock_li:
            self.cscores.append(0)
        self.old_cscores = list(self.cscores)
        # array of spacings for high scorers
        self.spaced = SpacedArray(self.num_divs_time)
        # undo settings
        self.is_undo = False
        self.is_equalize = False

    # EXP: for experiments
    def theta_set(self, theta):
        self.hl.set(theta)

    def get_wait(self):
        return self.wait_s

    def quit(self):
        return self.hsi.quit()

    def init_follow_up(self, clock_score_prior):
        # initialize
        self.init_round(False, True, clock_score_prior)
        ## history of click times
        self.clock_history = [[]]
        self.win_history = [-1]
        # whether the previous move was an "undo"
        self.just_undid = False
        ## bit rate initialize
        self.init_bits()

    def change_period(self, new_period):
        ## set the period
        self.time_rotate = new_period
        self.hsi.update_dens(new_period)

        ## related quantities
        # number of unique clock positions in the animation
        self.num_divs_time = int(numpy.ceil(self.time_rotate / config.ideal_wait_s))
        # reset wait_s so num_divs_time is integer
        self.wait_s = self.time_rotate / self.num_divs_time
        # find coordinates of hour hand positions
        self.hl = HourLocs(self.num_divs_time, self.radius)
        # array of spacings for high scorers
        self.spaced = SpacedArray(self.num_divs_time)

        ## restart rotation
        self.init_round(False, False, [])

    def get_histogram(self):
        return self.hsi.get_plot()

    def init_bits(self):
        self.bits_per_select = numpy.log(len(self.clocks_on)) / numpy.log(2)
        self.start_time = time.time()
        self.last_win_time = self.start_time
        self.num_bits = 0
        self.num_selects = 0

    def update_bits(self):
        self.num_selects += 1
        self.bits_per_select = numpy.log(len(self.clocks_on)) / numpy.log(2)
        self.num_bits += self.bits_per_select
        t = time.time()
        # if config.is_write_data:
        #	loc_rate = self.bits_per_select / (t - self.last_win_time)
        #	bit_rate = self.num_bits / (t - self.start_time)
        #	self.file_handle.write("bits " + str(bit_rate) + " " + str(loc_rate) + "\n")
        self.last_win_time = t

    def init_canvas_clocks(self):
        # list of IDs so can retrieve these objects to change them later
        self.circle_id = []
        self.noon_id = []
        self.hour_id = []
        for clock in self.clock_li:
            ## position coordinates
            # clock center
            x = self.centers[clock][0]
            y = self.centers[clock][1]
            # upper left corner
            ulx = x - self.radius
            uly = y - self.radius
            # lower right corner
            lrx = x + self.radius
            lry = y + self.radius
            ## create objects and record their IDs
            self.circle_id.append(self.canvas.create_oval([ulx, uly, lrx, lry], fill=config.circle_low_color,
                                                          outline=config.circle_outline_color))
            self.noon_id.append(
                self.canvas.create_line([x, y, x, uly], fill=config.noon_color, width=config.hand_width))
            self.hour_id.append(
                self.canvas.create_line([x, y, x, lry], fill=config.hour_color, width=config.hand_width))
        # blank out the clocks that aren't in use this round
        for clock in self.clocks_off:
            self.canvas.itemconfigure(self.circle_id[clock], fill=self.circle_off_color,
                                      outline=config.circle_off_color)
            self.canvas.itemconfigure(self.noon_id[clock], fill=config.circle_off_color)
            self.canvas.itemconfigure(self.hour_id[clock], fill=config.circle_off_color)

    # usually called after a timer increment in the parent program
    def increment(self, time_in):
        self.latest_time = time_in

        # update records
        for clock in self.clocks_on:
            # update time indices
            self.cur_hours[clock] = (self.cur_hours[clock] + 1) % self.num_divs_time
            # register in coordinates of hour hand
            v = self.hl.hour_locs[self.cur_hours[clock]]
            angle = math.atan2(v[1], v[0])
            self.parent.mainWidgit.clocks[clock].angle = angle + math.pi*0.5
            self.parent.mainWidgit.clocks[clock].repaint()


        # refresh the canvas
        # self.canvas.update_idletasks()

    # usually called after a keypress in the parent program
    def select(self, time_in):
        # update scores of each clock
        self.update_scores(time_in - self.latest_time)
        # update history of key presses
        if config.is_learning:
            self.update_history(time_in - self.latest_time)

        # proceed based on whether there was a winner
        if (self.is_winner()):
            # record winner
            self.win_history[0] = self.sorted_inds[0]
            # update number of bits recorded
            self.update_bits()
            # call parent program with choice
            (self.clocks_on, self.clocks_off, clock_score_prior, self.is_undo,
             self.is_equalize) = self.parent.make_choice(self.sorted_inds[0])
            # learn new scores
            if config.is_learning:
                self.learn_scores()
            self.parent.present_choice()
            # reset time indices
            self.init_round(True, False, clock_score_prior)
        else:
            # update time indices
            self.init_round(False, False, [])
            
            
        #Save all click time by the user
        
        last_gap_time = (time_in - self.last_press_time) % self.time_rotate
        self.save_click_time(last_gap_time)
        self.last_press_time = time_in
        print "click time was recorded!"

    #Save all click time by the user
    def save_click_time(self,last_gap_time):
        #time_diff_in = time_in - self.latest_time
        #No such thing as cur_hour
        #click_time = self.cur_hour*self.time_rotate*1.0/self.num_divs_time + time_diff_in - self.time_rotate*config.frac_period
        
        self.click_time_list.append(last_gap_time)

   

    def learn_scores(self):
        n_hist = len(self.clock_history)
        if (self.is_undo):
            # if just undid, delete the latest histories (history for this "undo" press and one before); 0:2 == [0,1]
            if (n_hist > 1):
                del self.clock_history[0:2]
                del self.win_history[0:2]
            else:
                self.clock_history = []
                self.win_history = []
            # (initial values inserted at end of this function)
        elif (n_hist > config.learn_delay):
            # index of the winning clock
            win_index = self.win_history[config.learn_delay]

            # add a score point to the location of each recorded press
            n_press = len(self.clock_history[config.learn_delay])
            for press in range(0, n_press):
                self.hsi.inc_score_inc(self.clock_history[config.learn_delay][press][win_index])

            # delete extra bits
            for index in range(n_hist - 1, config.learn_delay - 1, -1):
                self.clock_history.pop(index)
                self.win_history.pop(index)
        # move everything up by one
        self.clock_history.insert(0, [])
        self.win_history.insert(0, -1)

    def update_scores(self, time_diff_in):
        # add score for this round to cumulative score
        for clock in self.clocks_on:
            time_in = self.cur_hours[
                          clock] * self.time_rotate * 1.0 / self.num_divs_time + time_diff_in - self.time_rotate * config.frac_period
            self.cscores[clock] += self.hsi.get_score_inc(time_in)

        # sort the scores so as to ensure spacing between top scorers
        self.sorted_inds = list(self.clocks_on)
        self.sorted_inds.sort(self.compare_score)

    def update_history(self, time_diff_in):
        n_press = len(self.clock_history[0])
        self.clock_history[0].append([])
        i_all = 0
        i_on = 0
        while i_all < self.N_clocks:
            clock = self.clocks_on[i_on]
            if clock == i_all:
                click_time = (self.cur_hours[
                                  clock] * self.time_rotate * 1.0 / self.num_divs_time + time_diff_in - self.time_rotate * config.frac_period + 0.5) % 1 - 0.5  # mod and 0.5's for keeping in (-0.5,0.5) range
                self.clock_history[0][n_press].append(click_time)
                i_on += 1
            else:
                self.clock_history[0][n_press].append(0)
            i_all += 1

    # compares indices based on their cumulative score
    def compare_score(self, xind, yind):
        if (self.cscores[xind] < self.cscores[yind]):
            return 1
        elif (self.cscores[xind] > self.cscores[yind]):
            return -1
        else:
            return 0

    # determine if a single clock has won out above the rest
    def is_winner(self):
        loc_win_diff = self.win_diffs[self.sorted_inds[0]]
        if (len(self.clocks_on) <= 1):
            return True  # just for testing
        elif (self.cscores[self.sorted_inds[0]] - self.cscores[self.sorted_inds[1]] > loc_win_diff):
            return True
        else:
            return False

    def get_prior_magnitude(self):
        mag = self.hsi.get_magnitude()
        return mag

    def init_round(self, is_win, is_start, clock_score_prior):
        if (is_win or is_start):  # if won, restart everything
            if (is_win):
                # identify the undo button as the winner to highlight
                win_clock = self.sorted_inds[0]

            if (self.is_undo) and (not self.is_equalize):
                # recall the scores from last time
                ##self.cscores = list(self.old_scores)

                ##self.sorted_inds = list(self.clocks_on)
                ##self.sorted_inds.sort(self.compare_score)
                # median score as "delete" value
                ##median_cscore = self.cscores[self.sorted_inds[len(self.sorted_inds)/2]]
                # "delete" the highest scorer (send to lowest value)
                ##self.cscores[self.sorted_inds[0]] = median_cscore
                # set scores for non-zero entries of clock_score_prior
                ##count = 0
                ##for count in range(0,len(clock_score_prior)):
                ##	if(clock_score_prior[count] != 0):
                ##		self.cscores[self.clocks_on[count]] = self.cscores[self.sorted_inds[2]] # set to third highest score
                count = 0
                self.old_scores = list(self.cscores)
                for clock in self.clocks_on:
                    self.cur_hours[clock] = count % self.num_divs_time
                    self.cscores[clock] = 0

                    count += 1
                top_score = 0
            else:
                count = 0
                self.old_scores = list(self.cscores)
                for clock in self.clocks_on:
                    self.cur_hours[clock] = count % self.num_divs_time
                    self.cscores[clock] = clock_score_prior[count]
                    count += 1
                top_score = 0

        # update the sorted loading_text
        self.sorted_inds = list(self.clocks_on)
        self.sorted_inds.sort(self.compare_score)

        # OLD0: else: # if haven't won, restart according to score order
        # current: (always) restart according to score order
        ### NEW0: design improvement
        # if is_win or is_start:
        #	count = 0
        #	for clock in self.clocks_on: #when start, group close letters together
        #	    self.cur_hours[clock] = count % self.num_divs_time
        #	    count += 1
        # else:
        count = 0
        for sind in self.sorted_inds:
            self.cur_hours[sind] = self.spaced.arr[count % self.num_divs_time]
            count += 1

        if is_win or is_start:
            # handicap the highest scorer if it would be "inevitable" otherwise
            if (len(self.clocks_on) <= 1):
                pass
            elif (self.cscores[self.sorted_inds[0]] - self.cscores[self.sorted_inds[1]] > config.max_init_diff):
                self.cscores[self.sorted_inds[0]] = self.cscores[self.sorted_inds[1]] + config.max_init_diff
        top_score = self.cscores[self.sorted_inds[0]]

        # highlight all clockfaces "near" the winning score
        bound_score = top_score - self.win_diffs[self.sorted_inds[0]]
        for clock in self.clocks_on:

            if self.cscores[clock] > bound_score:
                self.parent.mainWidgit.clocks[clock].highlighted = True
                pass
                # self.canvas.itemconfigure(self.circle_id[clock], fill=config.circle_high_color, outline=outline_color,
                #                           width=cwidth)
            else:
                self.parent.mainWidgit.clocks[clock].highlighted = False
                pass
            #     self.canvas.itemconfigure(self.circle_id[clock], fill=config.circle_low_color, outline=outline_color,
            #                               width=cwidth)
            # self.canvas.itemconfigure(self.noon_id[clock], fill=config.noon_color, width=config.hand_width)
            # self.canvas.itemconfigure(self.hour_id[clock], fill=config.hour_color, width=config.hand_width)
            # turn off irrelevant faces
            self.parent.mainWidgit.clocks[clock].repaint()
        for clock in self.clocks_off:
            pass
            # self.canvas.itemconfigure(self.circle_id[clock], fill=config.circle_off_color,
            #                           outline=config.circle_off_color, width=config.circle_outline_width)
            # self.canvas.itemconfigure(self.noon_id[clock], fill=config.circle_off_color)
            # self.canvas.itemconfigure(self.hour_id[clock], fill=config.circle_off_color)
        # mark the winner
        # if(is_win):
        #    self.canvas.itemconfigure(self.circle_id[win_clock],outline=config.circle_win_color,width=config.circle_win_width)
        # register in coordinates of hour hand
        for clock in self.clocks_on:
            # x = self.centers[clock][0]
            # y = self.centers[clock][1]
            v = self.hl.hour_locs[self.cur_hours[clock]-1]
            angle = math.atan2(v[1], v[0])
            self.parent.mainWidgit.clocks[clock].angle = angle + math.pi*0.5
            self.parent.mainWidgit.clocks[clock].repaint()

        # update the canvas
        # self.canvas.update_idletasks()
