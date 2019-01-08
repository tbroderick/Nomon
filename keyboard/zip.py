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