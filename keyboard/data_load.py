import os
from pickle_util import PickleUtil
from matplotlib import pyplot as plt
from scipy import stats
import numpy as np

data_dir = "C:\\Users\\nickb\\AppData\\Local\\Nomon\\data"

click_data_files = []
click_context_files = []
preconfig_file = None
for path, dir, files in os.walk(data_dir):
    for file in files:
        if "click_time_log" in file:
            click_data_files += [os.path.join(path,file)]
        if "params_data_use_num" in file:
            click_context_files += [os.path.join(path,file)]
        if "preconfig" in file:
            preconfig_file = os.path.join(path,file)

raw_click_data = []
for data_file in click_data_files:
    data_handel = PickleUtil(data_file)
    raw_click_data += [data_handel.safe_load()]
    
context_data = []
for data_file in click_context_files:
    data_handel = PickleUtil(data_file)
    context_data += [data_handel.safe_load()]


def flatten(l):
    return [item for sublist in l for item in sublist]


class DataUtil:
    def __init__(self, data_dir):
        self.plot_colors = ["#0000ff", "#00aa00", "#aa0000", "#ff7700", "#aa00aa"]
        self.click_data_files = []
        self.click_context_files = []
        self.preconfig_file = None
        for path, dir, files in os.walk(data_dir):
            for file in files:
                if "click_time_log" in file:
                    self.click_data_files += [os.path.join(path, file)]
                if "params_data_use_num" in file:
                    self.click_context_files += [os.path.join(path, file)]
                if "preconfig" in file:
                    self.preconfig_file = os.path.join(path, file)

        self.rel_click_data = []
        self.abs_click_data = []
        self.speed_changes = []
        self.kde_list = []

        self.clicks_by_speed = {}
        self.corrected_clicks = None

    def load_data(self):
        # size_list = []
        for data_file in self.click_data_files:
            data_handel = PickleUtil(data_file)
            click_dict = data_handel.safe_load()
            # size_list += [len(click_dict["click time list"])]
            self.rel_click_data += [click[1] for click in click_dict["click time list"]]

        self.rel_click_data = np.array(self.rel_click_data)

        # size_list_2 = []
        for data_file in self.click_context_files:
            data_handel = PickleUtil(data_file)
            context_dict = data_handel.safe_load()
            self.abs_click_data += context_dict["press"]
            # size_list_2 += [len(flatten(context_dict["press"]))]
            self.speed_changes += context_dict["speed"]
        self.abs_click_data = np.array(flatten(self.abs_click_data))
        self.speed_changes.sort(key=lambda x: x[0])

        # print(self.click_context_files[14])
        # print(size_list)
        # print(size_list_2)

        preconfig_handel = PickleUtil(preconfig_file)
        preconfig = preconfig_handel.safe_load()
        self.kde_list = np.array(preconfig["li"])/np.sum(preconfig["li"])

        if len(self.abs_click_data) != len(self.rel_click_data):
            raise ValueError("Click data length does not match context data length!")
        print("Loaded " + str(len(self.abs_click_data)) + " clicks")

    def split_data(self):
        num_speed_changes = len(self.speed_changes)
        for change_index in range(num_speed_changes):
            time_min = self.speed_changes[change_index][0]
            if change_index == num_speed_changes-1:
                time_max = float("inf")
            else:
                time_max = self.speed_changes[change_index+1][0]

            clicks_int = np.array(np.where((self.abs_click_data > time_min) & (self.abs_click_data < time_max))[0],
                                  dtype='int64')

            matrix_index = np.vectorize(lambda m_index: self.rel_click_data[m_index])
            if clicks_int.size > 0:
                clock_speed = round(self.speed_changes[change_index][2], 2)
                clicks_rel_int = matrix_index(clicks_int)

                if clock_speed in self.clicks_by_speed.keys():
                    prev_clicks = self.clicks_by_speed[clock_speed]
                    self.clicks_by_speed[clock_speed] = np.concatenate((prev_clicks, clicks_rel_int))
                else:
                    self.clicks_by_speed[clock_speed] = clicks_rel_int

        print("Data partitioned into " + str(len(self.clicks_by_speed.keys())) + " sets by clock rotation speed")


    def correct_data(self):

        if 1.44 not in self.clicks_by_speed.keys():
            raise ValueError("Base rotation speed not in data!")

        base_clicks = self.clicks_by_speed[1.44]
        base_clicks_mean = np.mean(base_clicks)
        base_clicks = base_clicks - base_clicks_mean
        base_clicks_std = np.std(base_clicks)

        clock_speeds = list(self.clicks_by_speed.keys())
        self.corrected_clicks = []
        for clock_speed in clock_speeds:
            clicks = self.clicks_by_speed[clock_speed]
            clicks_mean = np.mean(clicks)
            clicks = clicks - clicks_mean
            clicks_std = np.std(clicks)
            clicks *= base_clicks_std/clicks_std

            self.corrected_clicks += clicks.tolist()

        self.corrected_clicks = np.array(self.corrected_clicks)


    def plot_data(self):
        fig = plt.figure()
        ax = plt.subplot(111)
        plot_num = 0
        for clock_speed in self.clicks_by_speed.keys():
            plot_color = self.plot_colors[plot_num]
            clicks = self.clicks_by_speed[clock_speed]
            clicks_mean = np.mean(clicks)
            clicks_std = np.std(clicks)
            clicks = clicks - clicks_mean

            plot_label = "speed: "+str(clock_speed)+" ("+str(len(clicks))+" points)"
            ax.hist(clicks+40, 80, range=[0, 80], density=True, color=plot_color, alpha=0.3, label=plot_label)

            kernel = stats.gaussian_kde(clicks)
            res = 10
            plt.plot(np.arange(80*res)/res, kernel(np.arange(80*res)/res-40), color=plot_color, linewidth=2)
            plot_num += 1

            plt.axvline(40, color=plot_color, linestyle="--", alpha=0.8)
            for i in [-1,1]:
                plt.axvline(40 + i*clicks_std, color=plot_color, linestyle=":", alpha=0.6)

        if self.corrected_clicks is not None:
            kernel = stats.gaussian_kde(self.corrected_clicks)
            res = 10
            plot_color = self.plot_colors[plot_num]
            plot_label = "speed_adj (" + str(len(self.corrected_clicks)) + " points)"
            plt.plot(np.arange(80 * res) / res, kernel(np.arange(80 * res) / res - 40), linestyle="--", color="0000", linewidth=2, label=plot_label)


        # ax.bar(np.arange(self.kde_list.size), self.kde_list, fill=False, edgecolor='black', label="KDE")
        ax.legend()
        ax.set_xlim(20,60)

        plt.show()


du = DataUtil(data_dir)
du.load_data()
du.split_data()
du.correct_data()
du.plot_data()