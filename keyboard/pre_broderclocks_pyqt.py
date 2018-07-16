from __future__ import division
import Tkinter
import numpy
import time
import broderclocks
import config
from PyQt4 import QtGui, QtCore
import math


class Pre_HourScoreIncs:
    def __init__(self, use_num, user_id, time_rotate, prev_data):
        # rotation period
        self.time_rotate = time_rotate
        # index over histogram bins
        self.index_li = range(0,config.num_divs_click)
        # location of histogram bins
        self.x_li = []
        for index in self.index_li:
            self.x_li.append(index*self.time_rotate/config.num_divs_click - self.time_rotate/2.0)
        
        #data points
        #pure press time around noon(operated to be around noon but still not index), just stored after every press
        self.y_li = []
        #number of traning examples
        self.n_training = 20
        
        
        #not even sure if we need this
        #Initialize the density histogram
        # we are not showing plots online so 
        # just collect the times and do a parzen window estimator at the end
        self.Z = 0
        self.dens_li = []
        self.opt_sig = 1

   #Calculate optimal bandwith for kernel density estimation
    def optimal_bandwith(self, things):
        return 1.06 * (self.n_training ** -0.2) * self.sample_std(things)
    
    #Calculate standard deviation of collected samples
    def sample_std(self, things):
        return numpy.std(things)
    
    #Do the actual kernel density estimation
    def calculate_density(self):
        #calculate density over all x locations and normalize them after
        #prop = 1.0 / self.n_training / self.optimal_bandwith()
        self.empirical = [self.index_into_compatible_with_xloc(self.yin_into_index(yin)) for yin in self.y_li]
        opt_sig = self.optimal_bandwith(self.empirical)
        self.opt_sig = opt_sig
        ##I think this line is the problem
        for x in self.x_li:
            x_loc = x
            #print "is yinto index nan?" + str(self.yin_into_index(self.y_li[0]))
            #print "is opt_sig squared nan?" + str(opt_sig**2)
            #print "is x_loc nan?" + str(x_loc)
            #print "is yin_into_index fucking up?" + str(self.yin_into_index(self.y_li[0]))
            #print "is it being compatible with x?" + str(self.index_into_compatible_with_xloc(self.yin_into_index(self.y_li[0])))
            #print "sum of normals " + str([self.normal(x_loc, self.index_into_compatible_with_xloc(self.yin_into_index(yin)), opt_sig**2) for yin in self.y_li]) 
            
            dens = sum([self.normal(x_loc, self.index_into_compatible_with_xloc(self.yin_into_index(yin)), opt_sig**2) for yin in self.y_li])
            #print "dens" + str(dens)
            self.dens_li.append(dens)
            self.Z += dens
        
        #empirical = [self.yin_into_index(yin) for yin in self.y_li ]
        #print "empirical is" + str(empirical)
        
        #self.dens_li = numpy.array(self.dens_li) / self.Z
        #self.dens_li = list(self.dens_li)
        return [self.dens_li, self.Z]
    
    def get_plot(self):
        return self.calculate_density()
    
    #Gaussian PDF. 
    def normal(self, x, mu, sig_sq):
        return numpy.exp(-((x-mu)**2)/(2*sig_sq)) / float(numpy.sqrt(2*numpy.pi*sig_sq))
    
    #Not sure if needed
    # return the click score for a particular press time
    #yin will be index!
    #MAYBE PROBLEM HERE
    def yin_into_index(self, yin):
        #yin_into_index = yin
        index = int(config.num_divs_click * (yin/self.time_rotate+0.5)) % config.num_divs_click
        return index
    
    def index_into_compatible_with_xloc(self, index):
        x_compat = index * self.time_rotate/config.num_divs_click - self.time_rotate/2.0
        return x_compat
    
class Pre_broderclocks:
    #Got rid of canvas
    def __init__(self, parent, file_handle, time_rotate, use_num, user_id, in_time, prev_data):
        self.parent = parent
        self.num_divs_time = int(numpy.ceil(time_rotate / config.ideal_wait_s))
        self.wait_s = time_rotate / self.num_divs_time
        self.time_rotate = time_rotate

        ##initialize like original broderclocks class##
        self.latest_time = in_time
        self.hl = broderclocks.HourLocs(self.num_divs_time, self.parent.radius)
        self.cur_hour = 0

        ## scores
        self.hsi = Pre_HourScoreIncs(use_num, user_id, time_rotate, prev_data)
        self.cscore = 0
        #it only needs to be 1 dimensional
        #Because the 2 more dimensions were for - many clocks, many clicks up until selection
        self.clock_history = []
        self.num_press = 0
        #Do I need this?
        #self.old_scores 
    
    def quit(self):
        return self.hsi.quit()
        
    def get_wait(self):
        return self.wait_s
    
    # usually called after a timer increment in the parent program
    def increment(self, time_in):
        self.latest_time = time_in

        
        # update time indices
        self.cur_hour = (self.cur_hour + 1) % self.num_divs_time
        # register in coordinates of hour hand
        x = self.parent.x
        y = self.parent.y
        v = self.hl.hour_locs[self.cur_hour]
        self.parent.v = v
        

        
        angle = math.atan2(v[1], v[0])
        self.parent.mainWidgit.clock.angle = angle + math.pi*0.5
        self.parent.mainWidgit.clock.repaint()

        
        self.parent.update()
            

        # refresh the canvas
        # self.canvas.update_idletasks()
        
    def select(self, time_in):
        # store the time of this last key press
        if config.is_pre_learning:
            self.num_press += 1
            #Need to do operation on the time_in
            time_diff_in = time_in - self.latest_time
            #I think we have no offset? But NEED TO CHECK
            ##NEEDS CHECKING
            #config.frac_period used nowhere but let's just do it cause they do it in the original code
            click_time = self.cur_hour*self.time_rotate*1.0/self.num_divs_time + time_diff_in - self.time_rotate*config.frac_period
            print "y_li will be appended by" + str(click_time)
            self.hsi.y_li.append(click_time)
            print "y_li is now" + str(self.hsi.y_li)
            #print self.hsi.y_li
        #initiate the clock again from noon
        #need to update self.lastest_time somewhere too
        self.init_round()
    
    def init_round(self):
        #put the needle at noon -> increment will animate
        self.cur_hour = 0
        #self.parent.gen_clock()
        self.parent.v = (0,self.parent.radius)
        self.latest_time = time.time()
    
        
        
    