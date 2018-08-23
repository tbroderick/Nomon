#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 16:09:10 2018

@author: TiffMin
"""
from __future__ import division
import random
from clock_inference_engine import *
from clock_util import *

import sys,os

import config
from pickle_util import *

class preClock_util(ClockUtil):
    def __init__(self, parent, bc, clock_inf):
        ClockUtil.__init__(self, parent, bc, clock_inf)
        self.cur_hour = 0
        #self.cur_hours = [0.0]*len(self.parent.dummy_clocks)
        self.bc = None
        self.pbc = bc
    
    
    def closest_in_hourloc(self, x, y):
        #이 라인을 CHECK하려면 look at notes
# =============================================================================
#         percent = (2 * math.pi + angle - math.pi/2) / (2 * math.pi)
#         percent = percent %1
#         ind1 = int(percent * len(self.hl.hour_locs))
# 
#         return ind1
# =============================================================================
        dist_list = [(h[0] -x)**2 + (h[1] -y)**2 for h in self.hl.hour_locs]
        return numpy.argmin(dist_list)
    
    #DOESNT MATTER WHERE YOU ROUND TO BECAUSE ANGLE RANDOM ANYWAYS
    #Find the index in hourloc
    def angle_into_cur_hour(self, clock_angle):
# =============================================================================
#         angle_decimal = angle / (2 * math.pi)
#         cur_hour = int(angle_decimal * self.num_divs_time)
#         return cur_hour
# =============================================================================
        angle = clock_angle - math.pi/2
        v = [math.cos(angle), math.sin(angle)]
        
        cur_hour = self.closest_in_hourloc(v[0], v[1])

        return cur_hour
    
    def increment(self):
        #for all the dummy clocks
        count = 0
        if self.parent.mainWidgit.highlight_clock:
             self.parent.mainWidgit.highlight()
        for clock in self.parent.mainWidgit.dummy_clocks:
            self.cur_hours[count] = (self.cur_hours[count] + 1) % self.num_divs_time
            if count == self.selected_clock:
                self.cur_hour = (self.cur_hour +1)  % self.num_divs_time
                self.cur_hours[count] =self.cur_hour
                self.latest_time = time.time()
            #clock.angle = self.parent.mainWidgit.clock.angle + clock.dummy_angle_offset
            # register in coordinates of hour hand
            v = self.hl.hour_locs[self.cur_hours[count]]
            angle = math.atan2(v[1], v[0])
            self.repaint_one_clock(count, angle)
            count +=1
            
        #for selected clock
        
    #NONEED FOR CHANGE PERIOD   
        
    def repaint_one_clock(self, clock_index, angle):        
        self.parent.mainWidgit.dummy_clocks[clock_index].angle = angle + math.pi*0.5
        self.parent.mainWidgit.dummy_clocks[clock_index].repaint()
        
   
    
    ####THIS IS EQUIVALENT TO THE CURHOUR만 하는 INITROUND   
    #IT REALLY IS EQUIVALENT TO INITROUND
    def redrawClocks(self):
        self.selected_clock = random.randint(0, 63)
        #self.selected_clock = 0
        count =0
        for clock in self.pbc.parent.mainWidgit.dummy_clocks:
            clock.setText("not me")
            clock.selected = False
            clock.highlighted = (random.random() < random.random())
            #나중에 여기 CHECK
            self.cur_hours[count] = random.choice(range(len(self.hl.hour_locs)))
            #clock.dummy_angle_offset = random.random() * math.pi* 2
            #angle = clock.dummy_angle_offset
            v = self.hl.hour_locs[self.cur_hours[count]]
            clock.angle = math.atan2(v[1], v[0]) + math.pi*0.5
            if count == self.selected_clock:
                self.cur_hour = random.choice(range(len(self.hl.hour_locs)))
                self.cur_hours[count] = self.cur_hour
                v = self.hl.hour_locs[self.cur_hours[count]]
                clock.angle = math.atan2(v[1], v[0]) + math.pi*0.5
                #clock.angle = 0
                clock.selected = True
                clock.setText("Click Me!")
            clock.repaint()
            count +=1
        self.latest_time = time.time()
        
        if self.pbc.parent.num_presses > 0:
            self.pbc.parent.mainWidgit.highlight_clock = True
            self.pbc.parent.mainWidgit.start_time = time.time()
             ###HERE
            #self.cur_hours[count] = self.angle_into_cur_hour(clock.angle)#should be index
            #count+=1
       
        #JUST FOR TESTING PURPOSES 
        #self.selected_clock = 0
        #self.pbc.parent.mainWidgit.dummy_clocks[self.selected_clock].angle = 0
        #self.cur_hour = self.angle_into_cur_hour(self.pbc.parent.mainWidgit.dummy_clocks[self.selected_clock].angle)
        
        
        
# =============================================================================
#     #CURHOUR만 하는 ㅑㅜㅑㅅ개ㅕ
#     def init_round(self):
#         ###SUBWINDOWS의 DUMMYCLOCKS should come in here
#         
# =============================================================================
        
        
        
class pretraining_inference:
    
    def __init__(self, parent, bc, past_data = None):
        self.parent = parent
        self.bc = bc
        self.clockutil = preClock_util(self.parent, self.bc, self)
        self.parent = parent
        self.time_rotate = self.parent.time_rotate
        self.kde = kernel_density_estimation(self.time_rotate)
        self.calc_density_called = False
        
        self.n_training = self.parent.total_presses
        
    def yin_into_index(self, yin):
        #yin_into_index = yin
        index = int(config.num_divs_click * (yin/self.time_rotate+0.5)) % config.num_divs_click
        return index
        
    def index_into_compatible_with_xloc(self, index):
        x_compat = index * self.time_rotate/config.num_divs_click - self.time_rotate/2.0
        return x_compat
    
    #Do the actual kernel density estimation
    def calculate_density(self):
        #THIS PART NEEDS TO BE FIXED? THIS CHECKING CONDITION. WHAT IF YOU NEED TO RETRAIN
        if self.n_training < len(self.kde.y_li):
            print "density already calculated; density needs to be reinitilazed if you want to recalculate"
            return [self.kde.dens_li, self.kde.Z]
        else:
            self.kde.initialize_dens()
        
            empirical = [self.index_into_compatible_with_xloc(self.yin_into_index(yin)) for yin in self.kde.y_li]
            self.kde.ksigma = self.kde.optimal_bandwith(empirical)
            
            count = 0
            for x_loc in self.kde.x_li:
                dens = sum([self.kde.normal(x_loc, self.index_into_compatible_with_xloc(self.yin_into_index(yin)), self.kde.ksigma**2) for yin in self.kde.y_li])
                self.kde.dens_li[count] = dens
                self.kde.Z += dens
                count += 1
            
            self.calc_density_called = True
            return [self.kde.dens_li, self.kde.Z]
        
class pre_broderclocks:
    
    def __init__(self, parent):
        self.parent = parent
        self.clock_inf = pretraining_inference(self.parent, self)
        
        self.time_rotate = self.parent.time_rotate
        self.num_divs_time = int(numpy.ceil(self.time_rotate / config.ideal_wait_s))
        self.latest_time = time.time()
        self.clock_inf.clockutil.redrawClocks()
        
        
      
    def select(self):
        ####CLOCKUTIL에서 달라진 INCREMTNT, 달라진 KDE, 달라진 SCOREFUNCTION 갖다 바꾸기
        #NEED TO CHANGE THIS LINE DEPENDING ON WHAT NICK DID
        
        if config.is_pre_learning:
            #Need to do operation on the time_in
            
            #I think we have no offset? But NEED TO CHECK
            ##NEEDS CHECKING
            #config.frac_period used nowhere but let's just do it cause they do it in the original code
            time_in = time.time()
            time_diff_in = time_in - self.clock_inf.clockutil.latest_time
            print "how much TIME tho" +  str(time_diff_in/self.time_rotate)
            percent = self.clock_inf.clockutil.cur_hour/len(self.clock_inf.clockutil.hl.hour_locs) + time_diff_in/self.time_rotate 
            index = int((percent *  len(self.clock_inf.kde.dens_li)) % len(self.clock_inf.kde.dens_li)) 
            click_time = self.clock_inf.kde.x_li[index] 
            
            #click_time = (self.clock_inf.clockutil.cur_hour*self.time_rotate*1.0/self.num_divs_time + time_diff_in - self.time_rotate*config.frac_period + 0.5) % 1 - 0.5
            print "y_li will be appended by" + str(click_time)
            self.clock_inf.kde.y_li.append(click_time)
            print "y_li is now" + str(self.clock_inf.kde.y_li)
            print "CURHOUR IS" + str(self.clock_inf.clockutil.cur_hour/len(self.clock_inf.clockutil.hl.hour_locs))
        self.init_round()
        
        
        
    def init_round(self):
        self.clock_inf.clockutil.redrawClocks()
        self.latest_time = time.time()
    
    #NEED TO FIX HERE LATER DEPENDING ON WHETHER PRETRAIN AGAIN WAS PRESSED OR NOT
    def save_when_quit(self):
        if self.clock_inf.calc_density_called == True:
            self.pretrain_data_path =  "data/preconfig_user_id"+ str(self.parent.sister.user_id)+ ".pickle" 
            PickleUtil(self.pretrain_data_path).safe_save({'li': self.clock_inf.kde.dens_li, 'z': self.clock_inf.kde.Z, 'opt_sig': self.clock_inf.kde.ksigma, 'y_li': [], 'yksigma':self.clock_inf.kde.y_ksigma})
        
    def quit_pbc(self):
        self.save_when_quit()
        
    