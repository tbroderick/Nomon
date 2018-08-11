#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 21:30:49 2018

@author: TiffMin
"""

from __future__ import print_function, division
import pickle, numpy
from pickle_util import *
import math

import matplotlib.pyplot as plt
def calc_mode(data_set):
    return data_set.index(max(data_set))

# =============================================================================
# def std_dev(data_set):
#     mean = sum([data_set[i]*i for i in range(len(data_set))])/sum(data_set)
#     print(mean)
#     sq_sum=0
#     for index in range(length):
#         sq_sum+=((index-mean)**2)*data_set[index]
#     return math.sqrt(sq_sum/(sum(data_set)-1))
# =============================================================================



#data = pickle.load(open("C:/Users/nickb/PycharmProjects/Nomon/keyboard/barsdump.p",'rb'))
#print(len(data))
pretrain_bars1 = PickleUtil("data/preconfig_train1.pickle").safe_load()['li']
pretrain_bars2 = PickleUtil("data/preconfig_train2.pickle").safe_load()['li']
main_bars1 = PickleUtil("data/preconfig_main1.pickle").safe_load()['li']
main_bars2 = PickleUtil("data/preconfig_main2.pickle").safe_load()['li']

pretrain_z1=PickleUtil("data/preconfig_train1.pickle").safe_load()['z']
pretrain_z2=PickleUtil("data/preconfig_train2.pickle").safe_load()['z']
main_z1=PickleUtil("data/preconfig_main1.pickle").safe_load()['z']
main_z2 = PickleUtil("data/preconfig_main2.pickle").safe_load()['z']





pretrain_avg = [100*(pretrain_bars1[i]/pretrain_z1+pretrain_bars2[i]/pretrain_z2) / 2.0 for i in range(len(pretrain_bars1))]
main_avg = [100*(main_bars1[i]/main_z1+main_bars2[i]/main_z2) / 2.0 for i in range(len(main_bars1))]

pretrain = pretrain_avg
actual = main_avg

length = len(pretrain)
height = max(pretrain + actual) * 1.1

modes = [0 for i in range(length)]
modes[calc_mode(pretrain)] = height
modes[calc_mode(actual)] = height

mp = calc_mode(pretrain)-40
ma = calc_mode(actual)-40
#sp = std_dev(pretrain)
#sa = std_dev(actual)



def std_dev(data):
    per = 2.215
    mean = sum([i*per/length*data[i] for i in range(len(data))])/100
    total = 0
    for i in range(len(data)):
        location = i*per/length
        total += data[i]/100 * (location - mean) **2 
    return math.sqrt(total / 1)

sp = std_dev(pretrain)
sa = std_dev(actual)


# plot histgrams
plt1 = plt.bar(range(int(-length/2), int(length/2)), actual, color='b', width=1, alpha=0.5)
plt2 = plt.bar(range(int(-length/2),int(length/2)), pretrain, color='r', width=1, alpha=0.5)

# plot modes
plt.plot([mp] * 2, [0, height*1.15], linewidth=2, color='r')
plt.plot([ma] * 2, [0, height*1.15], linewidth=2, color='b')

# plot std devs
plt.plot([mp + sp] * 2, [0, height], '--', color='r', alpha=0.75)
plt.plot([mp - sp] * 2, [0, height], '--', color='r', alpha=0.55)

plt.plot([ma + sa] * 2, [0, height], '--', color='b', alpha=0.75)
plt.plot([ma - sa] * 2, [0, height], '--', color='b', alpha=0.75)

plt.text(max(ma+sa, mp+sp) + 0.5, height * 0.8, "act " + u'\u03C3' + ' = ' + str(round(sa, 3)), color='b', fontsize=12)
plt.text(max(ma+sa, mp+sp) + 0.5, height * 0.75, "pre " + u'\u03C3' + ' = ' + str(round(sp, 3)), color='r', fontsize=12)

plt.text(max(ma, mp) + 0.5, height * 1.12, 'act mode = ' + str(ma), color='b', fontsize=12)
plt.text(max(ma, mp) + 0.5, height * 1.07, 'pre mode = ' + str(mp), color='r', fontsize=12)

plt.ylabel("Percentage (%)")
plt.xlabel("Time Difference from Noon (22.125 ms)")


plt.legend((plt1[0], plt2[0]), ('act', 'pre'))


plt.show()