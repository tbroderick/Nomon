import numpy
import config
#import click_distribution_inference_engine as inference


#Locations of MinuteHands
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
    def __init__(self, parent, inference):
        #parent is the widget
        self.parent = parent
        self.inference = inference
        self.cur_hours = []
        pass
    
    #cur_hours 
    def set_hourlocs(self):
        
        
    def change_period(self):
    
        
    def increment(self):
        
    #start the UI over
    def init_round(self):
        
    def highlight_clock(self, clock_index):
        pass
    
    def unhighlight_clock(self, clock_index):
        pass

