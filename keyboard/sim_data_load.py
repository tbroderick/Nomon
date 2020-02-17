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
from shutil import copyfile
from pickle_util import PickleUtil
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd

from scipy import stats
import numpy as np
from row_col_sim_data_load import SimDataUtil_row_col


class SimDataUtil:

    def __init__(self, data_dir):
        self.data_directory = data_dir
        self.data_by_user = self.load_data()
        self.user_numbers = set(self.data_by_user.keys())
        self.make_data_frame()

        self.plot_colors = ["#0000ff", "#00aa00", "#aa0000", "#ff7700", "#aa00aa"]

    def load_data(self):
        data_by_user = dict()
        for path, dir, files in os.walk(self.data_directory):
            user_dir = path[(len(self.data_directory)+1):]
            if user_dir is not "":
                if len(files) > 0:
                    user_data = dict()
                    for file in files:
                        file_data = PickleUtil(os.path.join(path, file)).safe_load()
                        if "dist_id" in file:
                            user_data["click_dist"] = file_data
                            self.click_dist = file_data
                            continue
                        else:
                            data_value_names = {'errors', 'selections', 'characters', 'presses_sel', 'presses_char',
                                                   'presses_word', 'kde_mses', 'kde'}
                            self.param_names = set(file_data.keys()) - data_value_names
                            params = tuple(file_data[name] for name in self.param_names)
                        # print(self.param_names)
                        # print(params)
                        user_data[params] = file_data
                    data_by_user[int(user_dir)] = user_data
        return data_by_user

    def plot_across_user(self, metric, params=None, trends=False, log=False, legend=None):
        if isinstance(metric, str):
            metric = [metric]
        for m in metric:
            dep_vars = []
            ind_vars = []
            for user in self.user_numbers:
                user_data = self.data_by_user[user]

                if params is None:
                    params = list(user_data.keys())[1]
                else:
                    if params not in user_data.keys():
                        raise KeyError("Parameters are not in saved data")

                if m not in user_data[params].keys():
                    raise KeyError("Metric is not in saved data")

                dep_vars += [user_data[params][m]]
                if "attribute" in user_data[params]:
                    if "supercloud_results_20" in self.data_directory:
                        ind_vars += [user_data[params]["attribute"]*4]
                    else:
                        ind_vars += [user_data[params]["attribute"]]
                else:
                    ind_vars += [user]

            data_points = list(zip(ind_vars, dep_vars))
            data_points.sort()
            ind_vars, dep_vars = zip(*data_points)

            if np.array(dep_vars[0]).size == 1:
                if log:
                    dep_vars = np.log(dep_vars)

                plt.plot(ind_vars, dep_vars)

            else:
                colors = np.arange(len(ind_vars))
                colors = colors/(len(ind_vars))
                if trends:
                    avg_grads = []
                    for i, line in enumerate(dep_vars):
                        label = ind_vars[i]
                        x_values = np.arange(line.size)+1
                        line_norm = line-np.min(line)

                        smoothing = 20
                        smooth_x = x_values[smoothing:-smoothing]
                        smooth_line = np.convolve(line_norm, np.ones((smoothing,))/smoothing)[smoothing:len(x_values)-smoothing]
                        # plt.plot(smooth_x, np.gradient(smooth_line), color=(min(1, (1-colors[i])*2),0,min(1, colors[i]*2)))
                        avg_grads += [-np.average(np.gradient(smooth_line))]
                    plt.plot(ind_vars[1:], avg_grads[1:] / np.max(avg_grads))
                else:
                    plt.figure(figsize=(10, 12))
                    x_pos = np.log(max([s.size for s in dep_vars])*1.05)
                    plt.xlim(np.log(4), x_pos*1.1)
                    max_y = -float("inf")
                    for i, line in enumerate(dep_vars[1:]):
                        label = ind_vars[i]
                        x_values = np.arange(line.size) + 1

                        if log:
                            line = np.log(line)
                        x_values = np.log(x_values)

                        max_y = max(max_y, max(line))

                        plt.plot(x_values[5:], line[5:],
                                 color=(min(1, (1 - colors[i]) * 2), 0, min(1, colors[i] * 2)))

                        y_pos = line[-1] - 0.0005

                        plt.text(x_pos, y_pos, str(label), fontsize=12, color=(min(1, (1 - colors[i]) * 2), 0, min(1, colors[i] * 2)))
                    if legend is not None:
                        plt.text(x_pos/1.075, max_y+abs(max_y*0.0075), legend["multi"], fontsize=11)

        if legend is not None:
            plt.title(legend["title"])
            plt.xlabel(legend["x"])
            plt.ylabel(legend["y"])
        plt.show()

    def make_data_frame(self):
        average_data = {}
        num_users = len(self.user_numbers)
        for user in self.user_numbers:
            user_data = self.data_by_user[user]
            for param in user_data:
                if param != "click_dist":
                    if param not in average_data:
                        average_data[param] = {'errors': [], 'selections': [], 'characters': [], 'presses_sel': [],
                                               'presses_char': []}
                    for data_label in ['selections', 'characters', 'presses_sel', 'presses_char', 'errors']:
                        average_data[param][data_label] += user_data[param][data_label]

        data_labels = {'errors', 'selections', 'characters', 'presses_sel', 'presses_char'}
        param_name_dict = {'num_words': "Word Predictions Max Count", 'time_rotate': "Time Rotate",
                           'win_diff': "Win Difference", 'N_pred': "Words Per Character",
                           'prob_thresh': "Probability Threshold", 'attribute': 'Attribute',
                           'false_positive': 'False Positive Rate'}
        var_name_dict = {'selections': "Selections/Min", 'characters': "Characters/Min",
                         'presses_char': "Clicks/Character",
                         'presses_sel': "Clicks/Selection", 'errors': "Error Rate"}

        long_form_data = []
        for params in average_data.keys():
            param_names = [param_name_dict[name] for name in self.param_names]
            observation = dict(zip(param_names, params))

            param_data = average_data[params]
            num_observations = len(param_data['errors'])

            for obs in range(num_observations):
                for data_label in data_labels:
                    observation[var_name_dict[data_label]] = param_data[data_label][obs]

                long_form_data += [observation.copy()]

        df = pd.DataFrame(long_form_data)
        self.DF = df

        self.average_DF = []
        time_rotates = list(set(self.DF["Time Rotate"]))
        time_rotates.sort(key=lambda x: x)

        for tr in time_rotates:
            DF = df[df["Time Rotate"] == tr]
            self.average_DF += [np.average(DF, axis=0)]
        self.average_DF = pd.DataFrame(self.average_DF, columns=self.DF.columns)
        self.average_DF["Time Rotate"] = np.round(self.average_DF["Time Rotate"], 2)

    def plot_across_params(self, params=None, sub_plot=None):

        ind_var_name = "Word Predictions Max Count"

        if params is None:
            params = ['Error Rate', 'Selections/Min', 'Characters/Min', 'Clicks/Selection',
                           'Clicks/Character', 'Error Rate']

        for dep_var_name in params:

            DF = self.DF
            pd.set_option('display.max_columns', 500)

            if sub_plot is None:
                fig, ax = plt.subplots()
            else:
                fig, ax = sub_plot

            fig.set_size_inches(10, 8)
            sns.set(font_scale=1.5, rc={"lines.linewidth": 3})
            sns.set_style({'font.serif': 'Helvetica'})
            if ind_var_name == "Word Predictions Max Count":
                sns.lineplot(x=ind_var_name, y=dep_var_name, hue="Words Per Character",
                             palette=sns.cubehelix_palette(1, start=2, rot=0.2, dark=.2, light=.7, reverse=True), data=DF, ci="sd")
            elif ind_var_name == "Left Context":

                sns.violinplot(x=ind_var_name, y=dep_var_name, hue="Left Context", data=DF, inner="points", figsize=(10, 8))

                lc_false = self.DF[self.DF[ind_var_name] == True][dep_var_name]
                lc_false_mean = np.mean(lc_false.values)
                plt.axhline(lc_false_mean, linestyle='--', color=(0.4, 0.4, 0.9))

                lc_true = self.DF[self.DF[ind_var_name] == False][dep_var_name]
                lc_true_mean = np.mean(lc_true.values)
                plt.axhline(lc_true_mean, linestyle='--', color=(0.9, 0.9, 0.4))

                t_value, p_value = stats.ttest_ind(lc_false, lc_true, equal_var=False)
                plt.text(0.9, -.1, 'p-value: '+str(round(p_value, 2)), ha='center', va='center', transform=ax.transAxes)

            elif ind_var_name == "Easy Corpus":
                sns.violinplot(x=ind_var_name, y=dep_var_name,
                            data=DF, ci="sd")

            else:
                hue_orders = list(set(self.DF["Time Rotate"]))
                hue_orders.sort(key=lambda x: x)
                sns.lineplot(x=ind_var_name, y=dep_var_name,
                             data=self.average_DF, ax=ax, legend=False, color="rosybrown", alpha=0.3, sort=False)

                g = sns.scatterplot(x=ind_var_name, y=dep_var_name, hue="Time Rotate",
                                    palette=sns.cubehelix_palette(len(hue_orders), start=0, rot=0.4, dark=.3, light=.7,
                                                                  reverse=False),
                                    data=self.average_DF, ax=ax, s=100, legend=False, label="Nomon")

                g.legend(loc='upper right',  ncol=1)

                leg = g.axes.get_legend()
                # change legend texts
                new_labels = ["Row Col Scan Delay", "Nomon Time Rotate"]
                for t, l in zip(leg.texts, new_labels): t.set_text(l)

                tr_min = self.average_DF["Time Rotate"][0]
                tr_min_x = self.average_DF[ind_var_name][0]
                tr_min_y = self.average_DF[dep_var_name][0]

                tr_max = self.average_DF["Time Rotate"][len(self.average_DF)-1]
                tr_max_x = self.average_DF[ind_var_name][len(self.average_DF)-1]
                tr_max_y = self.average_DF[dep_var_name][len(self.average_DF)-1]

                plt.text(tr_min_x - 1, tr_min_y + 0.25, str(tr_min)+" (s)", fontsize=12)
                plt.text(tr_max_x - 1, tr_max_y - 0.1, str(tr_max) + " (s)", fontsize=12)

            plt.title(dep_var_name+" vs. "+ind_var_name)

            plt.show()

        return fig, ax


def order_data(dir):
    click_dists = []
    if not os.path.exists(os.path.join(dir, "ordered_data")):
        os.mkdir(os.path.join(dir, "ordered_data"))

    for path, __, files in os.walk(dir):
        for file in files:
            if "dist_id" in file:
                click_dist = PickleUtil(os.path.join(path, file)).safe_load()
                if click_dist not in click_dists:
                    click_dists += [click_dist]
                    # os.mkdir(os.path.join(dir, os.path.join("ordered_data", str(click_dists.index(click_dist)))))
                print(path)
                plt.plot(click_dist)
                plt.show()


def main():
    # rc_sdu = SimDataUtil_row_col("C:\\Users\\nickb\\PycharmProjects\\Nomon\\keyboard\\sim_data")
    # rc_sdu.plot_across_params(params=['Error Rate'])
    # plt.show()

    # param = 'Error Rate'
    # param = 'Clicks/Character'
    # sub_plot = rc_sdu.plot_across_params(params=[param])

    sdu = SimDataUtil("C:\\Users\\Nicholas Bonaker\\PycharmProjects\\Nomon\\keyboard\\simulations\\param_opt\\sim_data")
    sdu.plot_across_params()


if __name__ == '__main__':
    main()
