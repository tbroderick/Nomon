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
import random
import math
from numpy import sin, cos, pi, argmin, ceil, where
import time
import os
from clock_inference_engine import KernelDensityEstimation
from clock_util import ClockUtil

import config
from pickle_util import PickleUtil


class PreClockUtil(ClockUtil):
    def __init__(self, parent, bc, clock_inf):
        ClockUtil.__init__(self, parent, bc, clock_inf)
        self.cur_hour = 0
        self.pbc = None
        self.pbc = bc
        self.selected_clock = random.randint(0, 63)

    def closest_in_hourloc(self, x, y):
        # 이 라인을 CHECK하려면 look at notes
        # =============================================================================
        #         percent = (2 * math.pi + angle - math.pi/2) / (2 * math.pi)
        #         percent = percent %1
        #         ind1 = int(percent * len(self.hl.hour_locs))
        #
        #         return ind1
        # =============================================================================
        dist_list = [(h[0] - x) ** 2 + (h[1] - y) ** 2 for h in self.hl.hour_locs]
        return argmin(dist_list)

    # DOESNT MATTER WHERE YOU ROUND TO BECAUSE ANGLE RANDOM ANYWAYS
    # Find the index in hourloc
    def angle_into_cur_hour(self, clock_angle):
        # =============================================================================
        #         angle_decimal = angle / (2 * math.pi)
        #         cur_hour = int(angle_decimal * self.num_divs_time)
        #         return cur_hour
        # =============================================================================
        angle = clock_angle - math.pi / 2
        v = [math.cos(angle), math.sin(angle)]

        cur_hour = self.closest_in_hourloc(v[0], v[1])

        return cur_hour

    def calcualte_clock_params(self, clock_type, recompute=False):

        if recompute:
            self.pbc.parent.clock_params[:, 0] = self.pbc.parent.clock_spaces[:, 1] / 2
            if clock_type == 'bar':
                self.pbc.parent.clock_params[:, 1] = self.pbc.parent.clock_spaces[:, 0] - 15
            else:
                self.pbc.parent.clock_params[:, 1] = self.pbc.parent.clock_spaces[:, 1] / 2 * 0.85
                
        if clock_type == 'default':
            # clock_params = array([[center_x = center_y, outer_radius, minute_x, minute_y] x num_clocks])
            self.pbc.parent.clock_params[:, 2] = self.pbc.parent.clock_params[:, 0] * (
                    1 + 0.7 * cos(self.clock_angles))
            self.pbc.parent.clock_params[:, 3] = self.pbc.parent.clock_params[:, 0] * (
                    1 + 0.7 * sin(self.clock_angles))

        elif clock_type == 'ball':
            # clock_params = array([[center_x = center_y, outer_radius, inner_radius] x num_clocks])
            self.pbc.parent.clock_params[:, 2] = self.pbc.parent.clock_params[:, 1]*(1-abs(self.clock_angles/pi + 0.5))

        elif clock_type == 'radar':
            # clock_params = array([[center_x = center_y, outer_radius, minute_angle1 ... minute_anglen] x num_clocks])
            inc_angle = 30
            self.pbc.parent.clock_params[:, 2] = (90 - self.clock_angles * 180. / math.pi)
            angle_correction = where(self.pbc.parent.clock_params[:, 2] > 0, -360, 0)
            self.pbc.parent.clock_params[:, 2] += angle_correction
            self.pbc.parent.clock_params[:, 2] *= 16
            for i in range(1, 6):
                self.pbc.parent.clock_params[:, 2 + i] = self.pbc.parent.clock_params[:, 2] - inc_angle * i * 16

        elif clock_type == 'pac_man':
            # clock_params = array([[center_x = center_y, outer_radius, minute_angle1] x num_clocks])
            self.pbc.parent.clock_params[:, 2] = -90 - (self.clock_angles * 180.) / math.pi
            angle_correction = where(self.pbc.parent.clock_params[:, 2] > 0, -360, 0)
            self.pbc.parent.clock_params[:, 2] += angle_correction
            self.pbc.parent.clock_params[:, 2] *= 16

        elif clock_type == 'bar':
            # clock_params = array([[center_x = center_y, bar_length, bar_position] x num_clocks])
            self.pbc.parent.clock_params[:, 2] = self.pbc.parent.clock_params[:, 1]*(1-abs(self.clock_angles/pi + 0.5))

    def increment(self):
        if self.parent.mainWidget.highlight_clock:
            self.parent.mainWidget.highlight()
        for clock in range(80):
            # update time indices
            self.cur_hours[clock] = (self.cur_hours[clock] + 1) % self.num_divs_time
            if clock == self.selected_clock:
                self.cur_hour = (self.cur_hour + 1) % self.num_divs_time
                self.cur_hours[clock] = self.cur_hour
                self.latest_time = time.time()

            self.clock_angles[clock] = self.hl.hour_locs[self.cur_hours[clock]][0]
            # self.repaint_one_clock(clock, clock_angles[clock])

        self.calcualte_clock_params(self.parent.clock_type)

        for clock in range(80):
            if self.parent.clock_type == 'default':
                self.parent.mainWidget.dummy_clocks[clock].set_params(self.pbc.parent.clock_params[clock, :4])
            elif self.parent.clock_type == 'ball':
                self.parent.mainWidget.dummy_clocks[clock].set_params(self.pbc.parent.clock_params[clock, :4])
            elif self.parent.clock_type == 'radar':
                self.parent.mainWidget.dummy_clocks[clock].set_params(self.pbc.parent.clock_params[clock, :])
            elif self.parent.clock_type == 'pac_man':
                self.parent.mainWidget.dummy_clocks[clock].set_params(self.pbc.parent.clock_params[clock, :4])
            elif self.parent.clock_type == 'bar':
                self.parent.mainWidget.dummy_clocks[clock].set_params(self.pbc.parent.clock_params[clock, :3])
            self.parent.mainWidget.dummy_clocks[clock].update()
    # NONEED FOR CHANGE PERIOD

    # THIS IS EQUIVALENT TO THE CURHOUR만 하는 INITROUND
    # IT REALLY IS EQUIVALENT TO INITROUND
    def redraw_clocks(self):
        same_clock = random.randint(0, 5)
        if same_clock < 3:
            self.selected_clock = random.randint(0, 63)
        # self.selected_clock = 0
        count = 0
        for clock in self.pbc.parent.mainWidget.dummy_clocks:
            clock.set_text("no")
            clock.selected = False
            clock.highlighted = (random.random() < random.random())
            # 나중에 여기 CHECK
            self.cur_hours[count] = random.choice(range(len(self.hl.hour_locs)))
            # clock.dummy_angle_offset = random.random() * math.pi* 2
            # angle = clock.dummy_angle_offset
            v = self.hl.hour_locs[self.cur_hours[count]]
            clock.angle = v[0] + math.pi * 0.5
            if count == self.selected_clock:
                self.cur_hour = random.choice(range(len(self.hl.hour_locs)))
                self.cur_hours[count] = self.cur_hour
                v = self.hl.hour_locs[self.cur_hours[count]]
                clock.angle = v[0] + math.pi * 0.5
                # clock.angle = 0
                clock.selected = True
                clock.set_text("Click!")
            clock.redraw_text = True
            count += 1
        self.latest_time = time.time()

        if self.pbc.parent.num_presses > 0:
            self.pbc.parent.mainWidget.highlight_clock = True
            self.pbc.parent.mainWidget.start_time = time.time()
            # HERE
            # self.cur_hours[count] = self.angle_into_cur_hour(clock.angle)#should be index
            # count+=1

        # JUST FOR TESTING PURPOSES
        # self.selected_clock = 0
        # self.pbc.parent.mainWidget.dummy_clocks[self.selected_clock].angle = 0
        # self.cur_hour = self.angle_into_cur_hour(self.pbc.parent.mainWidget.dummy_clocks[self.selected_clock].angle)


# =============================================================================
#     #CURHOUR만 하는 ㅑㅜㅑㅅ개ㅕ
#     def init_round(self):
#         ###SUBWINDOWS의 DUMMYCLOCKS should come in here
#         
# =============================================================================


class PretrainingInference:

    def __init__(self, parent, pbc, past_data=None):
        self.parent = parent
        self.pbc = pbc
        self.pre_clock_util = PreClockUtil(self.parent, self.pbc, self)
        self.parent = parent
        self.time_rotate = self.parent.time_rotate
        self.kde = KernelDensityEstimation(self.time_rotate)
        self.calc_density_called = False

        self.n_training = self.parent.total_presses

    def yin_into_index(self, yin):
        # yin_into_index = yin
        index = int(config.num_divs_click * (yin / self.time_rotate + 0.5)) % config.num_divs_click
        return index

    def index_into_compatible_with_xloc(self, index):
        x_compat = index * self.time_rotate / config.num_divs_click - self.time_rotate / 2.0
        return x_compat

    # Do the actual kernel density estimation
    def calculate_density(self):
        # THIS PART NEEDS TO BE FIXED? THIS CHECKING CONDITION. WHAT IF YOU NEED TO RETRAIN
        if self.n_training < len(self.kde.y_li):
            print("density already calculated; density needs to be reinitilazed if you want to recalculate")
            return [self.kde.dens_li, self.kde.Z]
        else:
            self.kde.initialize_dens()

            empirical = [self.index_into_compatible_with_xloc(self.yin_into_index(yin)) for yin in self.kde.y_li]
            self.kde.ksigma = self.kde.optimal_bandwith(empirical)

            count = 0
            for x_loc in self.kde.x_li:
                dens = sum([self.kde.normal(x_loc, self.index_into_compatible_with_xloc(self.yin_into_index(yin)),
                                            self.kde.ksigma ** 2) for yin in self.kde.y_li])
                self.kde.dens_li[count] = dens
                self.kde.Z += dens
                count += 1

            self.calc_density_called = True
            return [self.kde.dens_li, self.kde.Z]


class PreBroderClocks:

    def __init__(self, parent):
        self.parent = parent
        self.clock_inf = PretrainingInference(self.parent, self)

        self.time_rotate = self.parent.time_rotate
        self.num_divs_time = int(ceil(self.time_rotate / config.ideal_wait_s))
        self.latest_time = time.time()
        self.clock_inf.pre_clock_util.redraw_clocks()

    def select(self):
        # CLOCKUTIL에서 달라진 INCREMTNT, 달라진 KDE, 달라진 SCOREFUNCTION 갖다 바꾸기
        # NEED TO CHANGE THIS LINE DEPENDING ON WHAT NICK DID

        if config.is_pre_learning:
            # Need to do operation on the time_in

            # I think we have no offset? But NEED TO CHECK
            # NEEDS CHECKING
            # config.frac_period used nowhere but let's just do it cause they do it in the original code
            time_in = time.time()
            time_diff_in = time_in - self.clock_inf.pre_clock_util.latest_time
            print("how much TIME tho" + str(time_diff_in / self.time_rotate))
            percent = self.clock_inf.pre_clock_util.cur_hour / len(self.clock_inf.pre_clock_util.hl.hour_locs) \
                      + time_diff_in / self.time_rotate
            index = int((percent * len(self.clock_inf.kde.dens_li)) % len(self.clock_inf.kde.dens_li))
            click_time = self.clock_inf.kde.x_li[index]

            # click_time = (self.clock_inf.clock_util.cur_hour*self.time_rotate*1.0/self.num_divs_time + time_diff_in -
            # self.time_rotate*config.frac_period + 0.5) % 1 - 0.5
            print("y_li will be appended by" + str(click_time))
            self.clock_inf.kde.y_li.append(click_time)
            print("y_li is now" + str(self.clock_inf.kde.y_li))
            print("CURHOUR IS" + str(self.clock_inf.pre_clock_util.cur_hour / len(self.clock_inf.pre_clock_util.hl.hour_locs)))
        self.init_round()

    def init_round(self):
        self.clock_inf.pre_clock_util.redraw_clocks()
        self.latest_time = time.time()
        self.parent.init_clocks()

    # NEED TO FIX HERE LATER DEPENDING ON WHETHER PRETRAIN AGAIN WAS PRESSED OR NOT
    def save_when_quit(self):
        if self.clock_inf.calc_density_called:
            if self.parent.sister.user_cal_num == 0 and self.parent.sister.use_num == 0:
                new_cal_dir = self.parent.sister.data_handel
            else:
                new_cal_dir = self.parent.sister.user_handel+"\\cal"+str(self.parent.sister.user_cal_num+1)
                self.parent.sister.data_handel = new_cal_dir
                self.parent.sister.user_cal_num += 1
                os.mkdir(new_cal_dir)
                self.parent.sister.use_num = 0

            self.pretrain_data_path = new_cal_dir + "\\preconfig.p"
            PickleUtil(self.pretrain_data_path).safe_save({'li': self.clock_inf.kde.dens_li, 'z': self.clock_inf.kde.Z,
                                                           'opt_sig': self.clock_inf.kde.ksigma, 'y_li': [],
                                                           'yksigma': self.clock_inf.kde.y_ksigma})

    def quit_pbc(self):
        if not self.parent.sister.consent:
            if self.parent.sister.user_cal_num == 0 and self.parent.sister.use_num == 0:
                self.parent.sister.log_data_event()
                self.parent.sister.consent = True
        self.save_when_quit()
