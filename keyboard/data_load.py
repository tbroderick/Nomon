import os
from clock_inference_engine import KernelDensityEstimation
from pickle_util import PickleUtil
from matplotlib import pyplot as plt
import config
import numpy as np


user_num = 0

cwd = os.getcwd()
data_path = os.path.join(cwd, 'data')
data_path = os.path.join(data_path, str(user_num))
click_logs = []
for root, dirs, files in os.walk(data_path, topdown=False):
    for name in files:
        file_path = os.path.join(root, name)
        if "click_time_log" in name:
            data_handel = PickleUtil(file_path)
            data = data_handel.safe_load()
            click_logs += data['click time list']
press_times = []
press_locs = []
for log in click_logs:
    press_times += log['press times']
    press_locs += log['press locs']
clicks = np.array([press_locs, press_times]).T

time_rotate = config.period_li[12]
kde = KernelDensityEstimation(time_rotate)
kde.initialize_dens()

# increments and adds the new x to the ksigma calculation
n_hist = min(200, int(np.log(0.02) / np.log(kde.damp)))

def inc_score_inc(yin):
    # add to the list
    if len(kde.y_li) > n_hist:
        kde.y_li.pop()
        kde.y_ksigma.pop()
    kde.y_li.insert(0, yin)
    kde.y_ksigma.insert(0, kde.ksigma)
    # calculations
    kde.increment_dens(yin, kde.ksigma)
    kde.calc_ksigma(n_hist, min(kde.n_ksigma, len(kde.y_li)))

for i in range(40):
    inc_score_inc(clicks[i][0])
# print(kde.y_li)
plt.bar(np.arange(len(kde.dens_li)), kde.dens_li)

plt.show()