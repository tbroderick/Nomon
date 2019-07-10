import os
from shutil import copyfile
from pickle_util import PickleUtil
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd

from scipy import stats
import numpy as np


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
                        if "dist_id" in file:
                            user_data["click_dist"] = PickleUtil(os.path.join(path, file)).safe_load()
                        elif "npred" in file:
                            params = file.split("npred_")
                            params = [p.split("_nwords_") for p in params][1]
                            params = [p for sublist in params for p in sublist.split("_lcon_")]
                            params = [p for sublist in params for p in sublist.split(".p")][:3]
                            if len(params) == 2:
                                params = tuple([float(p) for p in params]+[1.0])
                            else:
                                params = tuple([float(p) for p in params])
                            user_data[params] = PickleUtil(os.path.join(path, file)).safe_load()
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
                                               'presses_char': [], 'presses_word': []}
                    for data_label in ['selections', 'characters', 'presses_sel', 'presses_char','presses_word', 'errors']:
                        average_data[param][data_label] += user_data[param][data_label]
        N_preds = list(set([param[0] for param in average_data]))
        N_preds.sort()
        N_preds.reverse()
        prob_threshs = list(set([param[1] for param in average_data]))
        prob_threshs.sort()
        if len(list(average_data.keys())[0]) > 2:
            left_contexts = list(set([param[2] for param in average_data]))
            left_contexts.sort()
        formatted_data_points = []
        for y_index, N_pred in enumerate(N_preds):
            sub_plot_values = []
            x_labels = []
            for x_index, prob_thresh in enumerate(prob_threshs):
                for z_index, l_cont in enumerate(left_contexts):
                    if (N_pred, prob_thresh, l_cont) in average_data:
                        if not isinstance(average_data[(N_pred, prob_thresh, l_cont)][data_label], int):
                            x_labels.append(str(int(prob_thresh)))

                            data_dict = average_data[(N_pred, prob_thresh, l_cont)]


                            all_data=[]
                            for key in ['selections', 'characters', 'presses_sel', 'presses_char', 'presses_word', 'errors']:
                                all_data += [data_dict[key]]
                            data_points = np.array(all_data).T

                            for points in data_points.tolist():
                                formatted_data_points.append(
                                    [prob_thresh, int(N_pred), bool(l_cont)]+points)

        df_columns = ["Word Predictions Max Count", "Words Per Character", "Left Context", "Selections per Minute",
                      "Characters per Minute", "Presses per Selection", "Presses per Character", "Presses per Word",
                      "Error Rate (Errors/Selection)"]
        df = pd.DataFrame(formatted_data_points, columns=df_columns)
        df["Selections per Word"] = df["Presses per Selection"]/df["Presses per Word"]
        self.DF = df

    def plot_across_params(self):

        ind_var_name = "Left Context"
        for data_label in ['selections','sel_word', 'characters', 'presses_sel', 'presses_char', 'presses_word', 'errors']:
            if data_label == 'selections':
                dep_var_name = "Selections per Minute"
            elif data_label == 'characters':
                dep_var_name = "Characters per Minute"
            elif data_label == 'presses_sel':
                dep_var_name = "Presses per Selection"
            elif data_label == 'presses_char':
                dep_var_name = "Presses per Character"
            elif data_label == 'presses_word':
                dep_var_name = "Presses per Word"
            elif data_label == 'sel_word':
                dep_var_name = "Selections per Word"
            elif data_label == 'errors':
                dep_var_name = "Error Rate (Errors/Selection)"
            else:
                raise ValueError("Data Attribute Unknown: " + data_label)

            DF = self.DF
            pd.set_option('display.max_columns', 500)

            fig, ax = plt.subplots()
            fig.set_size_inches(10, 8)
            sns.set(font_scale=1.5, rc={"lines.linewidth": 3})
            sns.set_style({'font.serif': 'Helvetica'})
            if ind_var_name == "Word Predictions Max Count":
                sns.lineplot(x=ind_var_name, y=dep_var_name, hue="Words Per Character",
                             palette=sns.cubehelix_palette(3, start=2, rot=0.2, dark=.2, light=.7, reverse=True), data=DF, ci="sd")
            elif ind_var_name == "Left Context":

                sns.violinplot(x=ind_var_name, y=dep_var_name, hue="Left Context", data=DF, inner="points", figsize=(10, 8))

                lc_false = self.DF[self.DF[ind_var_name] == True][dep_var_name]
                lc_false_mean = np.mean(lc_false.values)
                plt.axhline(lc_false_mean, linestyle='--', color=(0.4, 0.4, 0.9))

                lc_true = self.DF[self.DF[ind_var_name] == False][dep_var_name]
                lc_true_mean = np.mean(lc_true.values)
                plt.axhline(lc_true_mean, linestyle='--', color=(0.9, 0.9, 0.4))

                t_value, p_value = stats.ttest_ind(lc_false, lc_true, equal_var=False)
                plt.text(0.9, -.1, 'p-value: '+str(round(p_value,2)), ha='center', va='center', transform=ax.transAxes)

            else:
                sns.scatterplot(x=ind_var_name, y=dep_var_name, hue="Words Per Character",
                                palette=sns.cubehelix_palette(3, start=2, rot=0.2, dark=.2, light=.7, reverse=True), data=DF)


            plt.title("Unigram and N-gram LM: "+dep_var_name+" vs. "+ind_var_name)

            plt.show()

            # break

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

            # if "npred" in file:
            #     new_dir = os.path.join(dir, os.path.join("ordered_data", str(click_dists.index(click_dist))))
            #     if not os.path.exists(os.path.join(new_dir, file)):
            #         copyfile(os.path.join(path, file), os.path.join(new_dir, file))
            #     else:
            #         new_dir = os.path.join(dir, os.path.join("ordered_data", str(len(click_dists))))
            #         if not os.path.exists(new_dir):
            #             os.mkdir(new_dir)
            #         copyfile(os.path.join(path, file), os.path.join(new_dir, file))


def main():
    # sdu = SimDataUtil("simulations/increasing_variance/supercloud_results")
    # plot_legend = {"title": "MSE Improvement of Nomon KDE vs Click Distribution Variance", "x": "Standard Deviation (# hist bins)",
    #                "y": "Average (-) Gradient of MSE Over Presses"}
    # sdu.plot_across_user("kde_mses", (3, 0.008), trends=True, log=False, legend=plot_legend)

    sdu = SimDataUtil("simulations/language_model/supercloud_results_1")
    sdu.plot_across_params()

    # plot_legend = {"title": "MSE of Nomon KDE vs Bimodal Distance",
    #                "x": "log Number of Presses ( log(presses) )",
    #                "y": "MSE of KDE", "multi": "Modal Separation\n   (# hist bins)"}
    #
    # sdu.plot_across_user("kde_mses", (3, 0.008), trends=False, log=False, legend=plot_legend)

    # sdu.plot_across_user(["selections", "presses"], (3, 0.008))
    # sdu.plot_across_user("errors", (3, 0.008))

    # sdu.plot_across_user(["kde_mses", "errors"], (3, 0.008), trends=True)



if __name__ == '__main__':
    main()
