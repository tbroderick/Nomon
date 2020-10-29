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


from __future__ import division
from numpy import pi, zeros, ceil, cos, sin, where
import math
import time
import config
import kconfig


# Locations of MinuteHands
class HourLocs:
    def __init__(self, num_divs_time):

        self.num_divs_time = num_divs_time  # amount of time filling and emptying
        self.radius = 1

        self.hour_locs = []
        self.hl_base = []
        for index in range(0, num_divs_time):
            base = - pi / 2.0 + (2.0 * pi * index) / num_divs_time
            theta = -config.theta0 + base
            self.hour_locs.append([theta])
            self.hl_base.append(base)

    # EXP: for experimenting
    def set(self, theta):
        for index in range(0, self.num_divs_time):
            base = self.hl_base[index]
            self.hour_locs[index] = [self.radius * cos(-theta + base), self.radius * sin(-theta + base)]


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
            if insert_pt > 2 * (2 ** level - 1):
                insert_pt = 0
                level += 1
        self.rev_arr.insert(0, 0)

        self.arr = []
        for index in range(0, nels + 1):
            self.arr.append(0)
        for index in range(0, nels + 1):
            self.arr[self.rev_arr[index]] = index

        # Class related to the movement / highlight of clocks


class ClockUtil:

    # parent is the clock widget
    # Should have timers too
    def __init__(self, parent, bc, clock_inf):
        # parent is the widget
        self.parent = parent
        self.bc = bc
        self.clock_inf = clock_inf
        self.radius = kconfig.clock_rad
        if not self.bc.parent.is_simulation:
            if not self.parent.pretrain_window:
                self.cur_hours = [0.0] * len(self.parent.clock_centers)
            else:
                self.cur_hours = [0.0] * len(self.parent.mainWidget.dummy_clocks)
        else:
            self.cur_hours = [0.0] * len(self.parent.clock_centers)

        self.clock_angles = zeros(len(self.cur_hours))
        self.time_rotate = self.parent.time_rotate
        # LOOKATHERE
        self.num_divs_time = int(ceil(parent.time_rotate / config.ideal_wait_s))
        self.spaced = SpacedArray(self.num_divs_time)
        self.hl = HourLocs(self.num_divs_time)

        self.adt = [0, 0]
        # self.highlight_timer =

    # cur_hours
    # clocks_index_list can be actual clocks_on or sorted_inds(anyways list of indices)

    # =============================================================================
    #     def init_curhours(self, all_clocks_list):
    #         count = 0
    #         for sind in self.sorted_inds:
    #             self.cur_hours[sind] = self.spaced.arr[count % self.num_divs_time]
    #             count += 1
    # =============================================================================

    def update_curhours(self, update_clocks_list):
        count = 0
        for sind in update_clocks_list:
            self.cur_hours[sind] = self.spaced.arr[count % self.num_divs_time]
            count += 1

    # =============================================================================
    #     def set_curhours(self, whole_clock_list, clocks_on_list):
    #         self.cur_hours = [self.spaced.arr[i % self.num_divs_time] for i in range(len(whole_clock_list))]
    #
    # =============================================================================

    def change_period(self, new_period):
        # set the period
        # ONLY UPDATES CERTAIN METHODS CLOCKINFERENCEENGINE
        self.clock_inf.time_rotate = new_period
        self.clock_inf.update_dens(new_period)
        self.time_rotate = new_period
        # self.parent.time_rotate = new_period

        # related quantities
        # number of unique clock positions in the animation
        self.num_divs_time = int(ceil(self.time_rotate / config.ideal_wait_s))
        # reset wait_s so num_divs_time is integer
        # BUT DON"T REALLY SEEM TO USE THIS SO DON"T KNOW
        self.wait_s = self.time_rotate / self.num_divs_time
        # find coordinates of hour hand positions
        self.hl = HourLocs(self.num_divs_time)
        # array of spacings for high scorers
        self.spaced = SpacedArray(self.num_divs_time)

        # restart rotation
        # IS THIS JUST UPDATING CURHOURS OR ALSO CSCORES= JUST CURHOURS
        self.init_round(self.clock_inf.clocks_on)

    def increment(self, clock_index_list):
        if self.bc.parent.is_simulation:
            time_diff = self.bc.parent.time.time() - self.bc.latest_time
            # print("time diff", time_diff)
            self.bc.latest_time = self.bc.parent.time.time()
            for clock in clock_index_list:
                # update time indices
                self.cur_hours[clock] = (self.cur_hours[clock] + int(
                    time_diff / self.bc.parent.time_rotate * self.num_divs_time)) % self.num_divs_time
        else:
            if self.bc.parent.update_radii:
                self.bc.parent.update_clock_radii()
            # only update when pretrain=False (actual Nomon application)

            self.bc.latest_time = time.time()
            if not self.parent.pretrain:
                for clock in clock_index_list:
                    # update time indices
                    self.cur_hours[clock] = (self.cur_hours[clock] + 1) % self.num_divs_time

                for clock_index in clock_index_list:
                    clock = self.bc.parent.mainWidget.clockgrid_widget.clocks[clock_index]

                    angle = self.hl.hour_locs[self.cur_hours[clock_index]]
                    if clock is not None:
                        clock.angle = angle[0]
                self.bc.parent.mainWidget.clockgrid_widget.update()


    def set_radius(self, radius):
        self.radius = radius
        self.hl = HourLocs(self.num_divs_time)

    def repaint_clocks(self, clock_index_list, angle_for_each_clock):
        # sanity check
        if len(clock_index_list) != len(angle_for_each_clock):
            raise Exception("Arguments have different lengths!")
        else:
            for i in clock_index_list:
                self.parent.mainWidget.clocks[i].update()

    def repaint_one_clock(self, clock_index, angle):
        # self.parent.mainWidget.clocks[clock_index].angle = angle + math.pi*0.5
        # self.parent.mainWidget.clocks[clock_index].update()
        pass

    # start the UI over
    # DOCUMENT THIS WELL
    # whether is_win, is_start true or False, the locations , UI are all same
    def init_round(self, clock_index_list):
        self.update_curhours(clock_index_list)

    def highlight_clock(self, clock_index):
        if self.parent.mainWidget.clocks[clock_index] != '':
            clock = self.parent.mainWidget.clocks[clock_index]
            if self.bc.parent.word_pred_on == 1:
                if clock_index in self.bc.parent.mainWidget.reduced_word_clock_indices:
                    clock = self.bc.parent.mainWidget.reduced_word_clocks[
                        self.bc.parent.mainWidget.reduced_word_clock_indices.index(clock_index)]
            clock.selected = True
            clock.highlight_timer.start(2000)

    def unhighlight_clock(self, clock_index):
        if self.parent.mainWidget.clocks[clock_index] != '':
            clock = self.parent.mainWidget.clocks[clock_index]
            if self.bc.parent.word_pred_on == 1:
                if clock_index in self.bc.parent.mainWidget.reduced_word_clock_indices:
                    clock = self.bc.parent.mainWidget.reduced_word_clocks[
                        self.bc.parent.mainWidget.reduced_word_clock_indices.index(clock_index)]
            clock.selected = False
            clock.update()
            clock.stop()
