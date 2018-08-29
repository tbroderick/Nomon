#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 15:06:53 2018

@author: TiffMin
"""

from __future__ import division

import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import os, sys
sys.path.append(os.path.realpath('../keyboard'))
from clock_inference_engine import clock_inference 

# =============================================================================
# 
# #Just wrapped functions into a class so that 
# class ClicktimeSimulationFromGaussian:
# =============================================================================

#helper function to calulate value of normal pdf at x
def normal(x, mu, sig_sq):
    return np.exp(-((x-mu)**2)/(2*sig_sq)) / float(np.sqrt(2*np.pi*sig_sq))

#helper function to find expectation of x from p(x)
def get_mean(support_bars, distribution_bars):
    return round(np.average(support_bars, weights = distribution_bars),3)
    
#helper function to find std of x from p(x)
#Var[x] = E[(X - E[X])^2] = E[X^2] - E[X]^2
def get_std(support_bars, distribution_bars):
    Ex_sq = np.average([sp**2 for sp in support_bars], weights=distribution_bars)
    Ex = np.average(support_bars, weights = distribution_bars)
    return round(math.sqrt(Ex_sq - Ex**2),3)

#Sample num_sample points from a Gaussian of mean=mu, std=std
#Input: mu: the mean of the Gaussian we'd like to sample from
#       std: the standard deviation of the Gaussian we'd like to sample from
#       num_samples: number of samples we want
#Output: list of samples
def sample_from_gaussian(mu,std,num_samples,seednum):
    np.random.seed(seednum)
    return np.random.normal(mu,std,num_samples)


#A dummy parent temporarily created, just because clock_inf needs a parent to be initialized
class dummyParent:
    def __init__(self, time_rotate):
        self.time_rotate = time_rotate
        self.win_diffs = None
        self.clock_centers = [1]
        self.words_on = [1]
    

#Reconstructs a new distribution from the refactored branch's kerenel density estimation
#The kernel density estimation method used is "inc_score_inc" (line 188 of clock_inference_engine.py for Refactored)
#Input: sample_list: list of samples on the support (in the interval [-(rotation period)/2, (rotation period)/2])
#Output: the reconstructed distribution 
def reconstruct_refactored(sample_list):
    clock_inf = clock_inference(dummyParent(2), None, None) 
    for sample in sample_list:
        clock_inf.inc_score_inc(sample)
    return clock_inf.kde.dens_li
       


#The following imports are in try/except statements because they will only work in my local directories

try:
    sys.path.append(os.path.realpath('../../Nomon-08af0ede7cf5b7eeec71b4f983cf22cbb6dae896/keyboard'))
    from broderclocks import HourScoreIncs
except:
    print "This import does not work in your computer!"
 
#Reconstructs a new distribution from Tamara's original codebase's kerenel density estimation
#By Tamara's original codebase, I mean git commit 08af02de7c
#https://github.com/tbroderick/Nomon/blob/08af0ede7cf5b7eeec71b4f983cf22cbb6dae896/keyboard/broderclocks.py
#The kernel density estimation method used is "inc_score_inc" (line 123 of broderclocks.py)
#Input: sample_list: list of samples on the support (in the interval [-(rotation period)/2, (rotation period)/2])
#Output: the reconstructed distribution 
def kde_tamara(sample_list):
    try: 
        hsi = HourScoreIncs(0,0,2,None)
        for sample in sample_list:
            hsi.inc_score_inc(sample)
        return hsi.dens_li
    except:
        print "This function does not work in your computer (because of the imports)!"
        return None
        


#User modeling:
#Both of Tamara's original codebase and the Refactored version
#Starts with the base distribution Normal(0.05, 0.14**2)
#And use 2 seconds as default speed (Also the tech report follows these settings)

#mu = 0
#std = 0.2
mu = 0.05
std = 0.14

x_li = []
for index in range(0,80):
    x_li.append(index*2/80 - 2/2.0)

gaussian_density = [normal(x, mu, (std)**2) for x in x_li]/ sum([normal(x, mu, (std)**2) for x in x_li])
#[gaussian(x, 0, 2/3.92) for x in x_li]
#gaussian_density /= sum(gaussian_density)


#plot the ground truth in orange and the reconstructed sample in blue, in the same figure
def plot(num_samples):
    sample_list = sample_from_gaussian(0,2/3.92,num_samples,0)
    reconstructed = reconstruct_refactored(sample_list) / sum(reconstruct_refactored(sample_list))
    
    plt.figure()
    plt.title("Click Distribution Ground Truth/ Reconstructed with " +str(num_samples) + " Samples")
    plt.ylabel("Density Values")
    plt.plot(sample_list, [0]*len(sample_list), 'o', label="samples drawn")
    plt.plot(x_li, reconstructed, label="constructed from "+ str(num_samples) +" samples")
    plt.text(0.75, 0.03, 'reconstructed mean: ' +str(get_mean(x_li, reconstructed)) +'\n std: ' +str(get_std(x_li, reconstructed)), style='italic',
        bbox={'facecolor':'red'}  )
    plt.plot(x_li, gaussian_density, label="ground truth gaussian")
    plt.text(0.75, 0.05, 'ground thruth mean: ' +str(get_mean(x_li, reconstructed)) +'\n std: ' +str(get_std(x_li, reconstructed)), style='italic',
        bbox={'facecolor':'red'}  )
    plt.legend(loc='upper right')


    plt.savefig("figures/plot_with_"+str(num_samples)+"samples.jpg")

#plot the ground truth in orange and the reconstructed sample in blue, in the same figure
def plot_avg(num_samples):
    reconstructed = np.zeros(80)
    for seednum in range(30):
        sample_list = sample_from_gaussian(0,2/3.92,num_samples,seednum)
        reconstructed_current = np.array(reconstruct_refactored(sample_list)) / sum(reconstruct_refactored(sample_list))
        reconstructed += reconstructed_current
    reconstructed /= np.sum(reconstructed)
    plt.figure()
    plt.title("Click Distribution Ground Truth/ Reconstructed with " +str(num_samples) + " Samples")
    plt.ylabel("Density Values")
    plt.plot(x_li, reconstructed, label="constructed from "+ str(num_samples) +" samples")
    plt.text(0.75, 0.03, 'reconstructed mean: ' +str(get_mean(x_li, reconstructed)) +'\n std: ' +str(get_std(x_li, reconstructed)), style='italic',
        bbox={'facecolor':'red'}  )
    plt.plot(x_li, gaussian_density, label="ground truth gaussian")
    plt.text(0.75, 0.05, 'ground thruth mean: ' +str(get_mean(x_li, reconstructed)) +'\n std: ' +str(get_std(x_li, reconstructed)), style='italic',
        bbox={'facecolor':'red'}  )
    plt.legend(loc='upper right')
    plt.savefig("figures/avg_plot_with_"+str(num_samples)+"samples.jpg")

for i in range(0,30):
    plot(i)
    
for i in range(0,30):
    plot_avg(i)