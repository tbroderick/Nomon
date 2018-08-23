from __future__ import division
import numpy, math, time, sys, os
import config, kconfig
#import click_distribution_inference_engine as inference


#Locations of MinuteHands
class HourLocs:
    def __init__(self, num_divs_time):

        self.num_divs_time = num_divs_time  # amount of time filling and emptying
        self.radius = 1

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


#Class related to the movement / highlight of clocks
class ClockUtil:
    
    #parent is the clock widget
    #Should have timers too
    def __init__(self, parent, bc, clock_inf):
        #parent is the widget
        self.parent = parent
        self.bc = bc
        self.clock_inf = clock_inf
        self.radius = kconfig.clock_rad
        try:
            self.cur_hours = [0.0]*len(self.parent.clock_centers)
        except:
            self.cur_hours = [0.0]*len(self.parent.mainWidgit.dummy_clocks)
        self.time_rotate = self.parent.time_rotate 
        ###LOOKATHERE
        self.num_divs_time = int(numpy.ceil(parent.time_rotate / config.ideal_wait_s))
        self.spaced = SpacedArray(self.num_divs_time)
        self.hl = HourLocs(self.num_divs_time)
        #self.highlight_timer = 
        
    
    #cur_hours 
    #clocks_index_list can be actual clocks_on or sorted_inds(anyways list of indices)

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
        ## set the period
        #ONLY UPDATES CERTAIN METHODS CLOCKINFERENCEENGINE
        self.clock_inf.time_rotate = new_period
        self.clock_inf.update_dens(new_period)
        self.time_rotate = new_period
        self.parent.time_rotate = new_period

        ## related quantities
        # number of unique clock positions in the animation
        self.num_divs_time = int(numpy.ceil(self.time_rotate / config.ideal_wait_s))
        # reset wait_s so num_divs_time is integer
        #BUT DON"T REALLY SEEM TO USE THIS SO DON"T KNOW
        self.wait_s = self.time_rotate / self.num_divs_time
        # find coordinates of hour hand positions
        self.hl = HourLocs(self.num_divs_time)
        # array of spacings for high scorers
        self.spaced = SpacedArray(self.num_divs_time)

        ## restart rotation
        #IS THIS JUST UPDATING CURHOURS OR ALSO CSCORES= JUST CURHOURS
        self.init_round(self.clock_inf.clocks_on)
        
        
    
    #time_in is the pressed time
    def increment(self, clock_index_list):
        #only update when pretrain=False (actual Nomon application)
        self.bc.latest_time = time.time()
        if not self.parent.pretrain:
            for clock in clock_index_list:
                # update time indices
                self.cur_hours[clock] = (self.cur_hours[clock] + 1) % self.num_divs_time
                # register in coordinates of hour hand
                v = self.hl.hour_locs[self.cur_hours[clock]]
                angle = math.atan2(v[1], v[0])
                self.repaint_one_clock(clock, angle)
            
                
    def set_radius(self, radius):
        self.radius = radius
        self.hl = HourLocs(self.num_divs_time)
        
    
    def repaint_clocks(self, clock_index_list, angle_for_each_clock):
        #sanity check
        if len(clock_index_list) != len(angle_for_each_clock):
            raise Exception("Arguments have different lengths!")
            
        else:
            for i in range(len(clock_index_list)):
                clock_index, angle = clock_index_list[i], angle_for_each_clock[i]
                self.parent.mainWidgit.clocks[clock_index].angle = angle + math.pi*0.5
                self.parent.mainWidgit.clocks[clock_index].repaint()
    
    def repaint_one_clock(self, clock_index, angle):        
        self.parent.mainWidgit.clocks[clock_index].angle = angle + math.pi*0.5
        self.parent.mainWidgit.clocks[clock_index].repaint()
        
    
    #start the UI over
    #DOCUMENT THIS WELL
    #whether is_win, is_start true or False, the locations , UI are all same
    def init_round(self, clock_index_list):
        self.update_curhours(clock_index_list)
        for clock in clock_index_list:
            #THINK THIS IS WRONG. The -1
            #v = self.hl.hour_locs[self.cur_hours[clock]-1]
            self.cur_hours[clock]-1
            v = self.hl.hour_locs[self.cur_hours[clock]-1]
            angle = math.atan2(v[1], v[0])
            self.repaint_one_clock(clock, angle)
        
        
    def highlight_clock(self, clock_index):
        if self.parent.mainWidgit.clocks[clock_index] != '':
            self.parent.mainWidgit.clocks[clock_index].selected = True
            self.parent.mainWidgit.clocks[clock_index].repaint()
            self.parent.mainWidgit.highlight_timer.start(2000)
    
    def unhighlight_clock(self, clock_index):
        if self.parent.mainWidgit.clocks[clock_index] != '':
            self.parent.mainWidgit.clocks[clock_index].selected = False
            self.parent.mainWidgit.clocks[clock_index].repaint()
            self.parent.mainWidgit.highlight_timer.stop()
    