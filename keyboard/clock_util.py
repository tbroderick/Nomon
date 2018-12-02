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
        if not self.parent.pretrain_window:
            self.cur_hours = [0.0]*len(self.parent.clock_centers)
        else:
            self.cur_hours = [0.0]*len(self.parent.mainWidgit.dummy_clocks)
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
        self.parent.time_rotate = new_period

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

    def calcualte_clock_params(self, clock_type, recompute=False):
        if recompute:
            self.bc.parent.clock_params[:, 0] = self.bc.parent.clock_spaces[:, 1]/2
            if clock_type == 'bar':
                self.bc.parent.clock_params[:, 1] = self.bc.parent.clock_spaces[:, 0] - 15
            else:
                self.bc.parent.clock_params[:, 1] = self.bc.parent.clock_spaces[:, 1] / 2 * 0.85

        if clock_type == 'default':
            # clock_params = array([[center_x = center_y, outer_radius, minute_x, minute_y] x num_clocks])
            self.bc.parent.clock_params[:, 2] = self.bc.parent.clock_params[:, 0] * (
                        1 + 0.7 * cos(self.clock_angles))
            self.bc.parent.clock_params[:, 3] = self.bc.parent.clock_params[:, 0] * (
                        1 + 0.7 * sin(self.clock_angles))

        elif clock_type == 'ball':
            # clock_params = array([[center_x = center_y, outer_radius, inner_radius] x num_clocks])
            self.bc.parent.clock_params[:, 2] = self.bc.parent.clock_params[:, 1]*(1-abs(self.clock_angles/pi + 0.5))

        elif clock_type == 'radar':
            # clock_params = array([[center_x = center_y, outer_radius, minute_angle1 ... minute_anglen] x num_clocks])
            inc_angle = 30
            self.bc.parent.clock_params[:, 2] = (90 - self.clock_angles * 180. / math.pi)
            angle_correction = where(self.bc.parent.clock_params[:, 2] > 0, -360, 0)
            self.bc.parent.clock_params[:, 2] += angle_correction
            self.bc.parent.clock_params[:, 2] *= 16
            for i in range(1, 6):
                self.bc.parent.clock_params[:, 2 + i] = self.bc.parent.clock_params[:, 2] - inc_angle * i * 16

        elif clock_type == 'pac_man':
            # clock_params = array([[center_x = center_y, outer_radius, minute_angle1] x num_clocks])
            self.bc.parent.clock_params[:, 2] = -90 - (self.clock_angles * 180.) / math.pi
            angle_correction = where(self.bc.parent.clock_params[:, 2] > 0, -360, 0)
            self.bc.parent.clock_params[:, 2] += angle_correction
            self.bc.parent.clock_params[:, 2] *= 16

        elif clock_type == 'bar':
            # clock_params = array([[center_x = center_y, bar_length, bar_position] x num_clocks])
            self.bc.parent.clock_params[:, 2] = self.bc.parent.clock_params[:, 1]*(1-abs(self.clock_angles/pi + 0.5))

    def increment(self, clock_index_list):
        if self.bc.parent.update_radii:
            self.bc.parent.update_clock_radii()
        # only update when pretrain=False (actual Nomon application)

        self.bc.latest_time = time.time()
        if not self.parent.pretrain:
            for clock in clock_index_list:
                # update time indices
                self.cur_hours[clock] = (self.cur_hours[clock] + 1) % self.num_divs_time
                # register in coordinates of hour hand
                self.clock_angles[clock] = self.hl.hour_locs[self.cur_hours[clock]][0]
                # self.repaint_one_clock(clock, clock_angles[clock])


            self.calcualte_clock_params(self.bc.parent.clock_type)
            for clock_index in clock_index_list:
                clock = self.bc.parent.mainWidgit.clocks[clock_index]

                if self.bc.parent.word_pred_on == 1:
                    if clock_index in self.bc.parent.mainWidgit.reduced_word_clock_indices:
                        clock = self.bc.parent.mainWidgit.reduced_word_clocks[
                            self.bc.parent.mainWidgit.reduced_word_clock_indices.index(clock_index)]

                if self.bc.parent.clock_type == 'default':
                    clock.set_params(self.bc.parent.clock_params[clock_index, :4])
                elif self.bc.parent.clock_type == 'ball':
                    clock.set_params(self.bc.parent.clock_params[clock_index, :4])
                elif self.bc.parent.clock_type == 'radar':
                    clock.set_params(self.bc.parent.clock_params[clock_index, :])
                elif self.bc.parent.clock_type == 'pac_man':
                    clock.set_params(self.bc.parent.clock_params[clock_index, :4])
                elif self.bc.parent.clock_type == 'bar':
                    clock.set_params(self.bc.parent.clock_params[clock_index, :3])
                clock.update()


    def set_radius(self, radius):
        self.radius = radius
        self.hl = HourLocs(self.num_divs_time)
    
    def repaint_clocks(self, clock_index_list, angle_for_each_clock):
        # sanity check
        if len(clock_index_list) != len(angle_for_each_clock):
            raise Exception("Arguments have different lengths!")
        else:
            for i in clock_index_list:
                self.parent.mainWidgit.clocks[i].update()
    
    def repaint_one_clock(self, clock_index, angle):        
        self.parent.mainWidgit.clocks[clock_index].angle = angle + math.pi*0.5
        self.parent.mainWidgit.clocks[clock_index].update()

    # start the UI over
    # DOCUMENT THIS WELL
    # whether is_win, is_start true or False, the locations , UI are all same
    def init_round(self, clock_index_list):
        self.update_curhours(clock_index_list)
        for clock in clock_index_list:
            # THINK THIS IS WRONG. The -1
            # v = self.hl.hour_locs[self.cur_hours[clock]-1]
            self.cur_hours[clock]-1
            v = self.hl.hour_locs[self.cur_hours[clock]-1]
            angle = v[0]
            self.repaint_one_clock(clock, angle)

    def highlight_clock(self, clock_index):
        if self.parent.mainWidgit.clocks[clock_index] != '':
            clock = self.parent.mainWidgit.clocks[clock_index]
            if self.bc.parent.word_pred_on == 1:
                if clock_index in self.bc.parent.mainWidgit.reduced_word_clock_indices:
                    clock = self.bc.parent.mainWidgit.reduced_word_clocks[
                        self.bc.parent.mainWidgit.reduced_word_clock_indices.index(clock_index)]
            clock.selected = True
            clock.highlight_timer.start(2000)
    
    def unhighlight_clock(self, clock_index):
        if self.parent.mainWidgit.clocks[clock_index] != '':
            clock = self.parent.mainWidgit.clocks[clock_index]
            if self.bc.parent.word_pred_on == 1:
                if clock_index in self.bc.parent.mainWidgit.reduced_word_clock_indices:
                    clock = self.bc.parent.mainWidgit.reduced_word_clocks[
                        self.bc.parent.mainWidgit.reduced_word_clock_indices.index(clock_index)]
            clock.selected = False
            clock.update()
            clock.stop()
