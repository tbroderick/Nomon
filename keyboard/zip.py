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



import os
import zipfile
from pickle_util import PickleUtil
from matplotlib import pyplot as plt
import numpy as np

cwd = os.getcwd()
data_path = os.path.join(cwd, 'data')
# data_path = os.path.join(data_path, '0')
# data_handel = os.path.join(data_path, 'cal0')
#
# preconfig_path = os.path.join(data_handel, 'preconfig.p')
# preconfig_pickle = PickleUtil(preconfig_path)
# preconfig_data = preconfig_pickle.safe_load()
#
# clicks = np.array(preconfig_data['y_li'])
# circle = plt.Circle((0, 0), 1, color='b', fill=False)
# fig, ax = plt.subplots()
# ax.add_patch(circle)
# ax.scatter(np.cos(-clicks*4+np.pi/2), np.sin(-clicks*4+np.pi/2), color='purple')
# ax.plot([0,0], [0,1], color='red', linewidth=2, markersize=12)
# for i in range(80):
#     ax.plot([np.cos(np.pi/40*i)*0.9, np.cos(np.pi/40*i)], [np.sin(np.pi/40*i)*0.9, np.sin(np.pi/40*i)], color='black', linewidth=1, linestyle='dashed', markersize=12)
# ax.set_aspect('equal', adjustable='datalim')
# ax.plot()
# plt.show()
#
# plt.bar(list(range(80)),np.array(preconfig_data['li'])/np.sum(np.array(preconfig_data['li'])))
# plt.show()

zf = zipfile.ZipFile("nomon_data.zip", "w")
for dirname, subdirs, files in os.walk("data"):
    zf.write(dirname)
    for filename in files:
        zf.write(os.path.join(dirname, filename))
zf.close()