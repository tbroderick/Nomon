import os
from pickle_util import PickleUtil
from matplotlib import pyplot as plt
from scipy import stats
import seaborn as sns
import pandas as pd
from config import period_li, default_rotate_ind
from phrases import Phrases
from text_stats import calc_MSD
import numpy as np

# data_dir = "D:\\Users\\nickb\\Study Data\\nomon_data\\951"
# data_dir2 = "D:\\Users\\nickb\\Study Data\\row_col_data\\951"
data_dir = "C:\\Users\\nickb\\AppData\\Local\\Nomon\\data\\999"
data_dir2 = "C:\\Users\\nickb\\AppData\\Local\\RowCol\\data\\100"


def flatten(l):
    return [item for sublist in l for item in sublist]


class DataUtil:
    def __init__(self, data_dir):
        self.phrase_util = Phrases("resources/comm2.dev")
        self.plot_colors = ["#0000ff", "#4400ff", "#8800ff", "#cc00ff", "#ff00cc", "#ff0088", "#ff0044"]
        self.click_data_files = []
        self.click_context_files = []
        self.preconfig_file = None
        self.data_dir = data_dir
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
        self.selection_data = []
        self.speed_changes = []
        self.kde_list = []

        self.clicks_by_speed = {}
        self.clicks_by_phrase = {}
        self.phrase_stats = {}
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
            self.selection_data += context_dict["choice"]

        self.abs_click_data = np.array(flatten(self.abs_click_data))
        self.speed_changes.sort(key=lambda x: x[0])


        if self.preconfig_file is not None:
            preconfig_handel = PickleUtil(self.preconfig_file)
            preconfig = preconfig_handel.safe_load()
            self.kde_list = np.array(preconfig["li"])/np.sum(preconfig["li"])

        if len(self.abs_click_data) != len(self.rel_click_data):
            raise ValueError("Click data length does not match context data length!")
        print("Loaded " + str(len(self.abs_click_data)) + " clicks")

    def split_data_phrase(self):
        self.phrases = []
        self.phrase_times = {}
        phrase_start = 0
        uncorrected_error = 0
        corrected_error = 0
        session_num = 0
        start_time_prev = 0
        phrase_selections = 0

        for selection_num, selection in enumerate(self.selection_data):  # scan through data to find phrases & time ints
            if "target" in selection:
                phrase = selection["target"]
                typed = selection["typed"]
                is_backspace = selection["backspace"]
                is_undo = selection["undo"]

                if phrase not in self.phrases:
                    self.phrases.append(phrase)
                    phrase_start = selection["time"]

                phrase_selections += 1

                if is_backspace:  # accumulate corrected errors
                    corrected_error += 1
                if is_undo:
                    if selection_num > 0:
                        # prev_typed = self.selection_data[selection_num-1]["typed"]
                        # typed_difference = prev_typed[len(typed):]
                        corrected_error += 1

                _, completed_phrase = self.phrase_util.compare(typed, phrase)
                if completed_phrase and not is_undo:
                    self.phrase_times[phrase] = (phrase_start, selection["time"])
                    uncorrected_error = calc_MSD(typed, phrase)[0]
                    total_error = (uncorrected_error + corrected_error) / len(max(typed, phrase))

                    self.phrase_stats[phrase] = {"error_unc": uncorrected_error, "error_cor": corrected_error,
                                                 "error_tot": total_error, "selections": phrase_selections}

                    corrected_error = 0
                    phrase_selections = 0

        self.phrases = list(self.phrase_times.keys())
        self.phrases.sort(key=lambda x: self.phrase_times[x][0])

        print("Data partitioned into " + str(len(self.phrases)) + " sets by phrase")

        for phrase in self.phrases:  # split data according to phrase times calculated above
            phrase_start, phrase_end = self.phrase_times[phrase]
            phrase_click_indices = np.where((self.abs_click_data >= phrase_start) & (self.abs_click_data <= phrase_end))
            phrase_abs_clicks = self.abs_click_data[phrase_click_indices]
            phrase_rel_clicks = self.rel_click_data[phrase_click_indices]

            if len(phrase_abs_clicks) > 0:
                first_click_time = min(phrase_abs_clicks)

                self.clicks_by_phrase[phrase] = {"abs": phrase_abs_clicks, "rel": phrase_rel_clicks}
                stat_dict = self.phrase_stats[phrase]

                num_clicks = len(phrase_abs_clicks)
                time_int = phrase_end - first_click_time
                num_characters = len(phrase)
                num_words = len(phrase.split(" "))
                num_sel = stat_dict["selections"]


                clicks_per_char = num_clicks / num_characters
                clicks_per_word = num_clicks / num_words
                clicks_per_sel = num_sel / num_words
                chars_per_min = num_characters / time_int * 60
                words_per_min = num_words / time_int * 60
                sel_per_min = num_sel / time_int * 60


                stat_dict["clicks_char"] = clicks_per_char
                stat_dict["clicks_word"] = clicks_per_word
                stat_dict["clicks_sel"] = clicks_per_sel
                stat_dict["chars_min"] = chars_per_min
                stat_dict["words_min"] = words_per_min
                stat_dict["sel_min"] = sel_per_min

                if phrase_start - start_time_prev > 20 * 60:
                    session_num += 1
                start_time_prev = phrase_start

                stat_dict["session"] = session_num
                stat_dict["start_time"] = phrase_start

            else:
                del self.phrase_stats[phrase]

            self.phrases = list(self.phrase_stats.keys())

        # print(self.phrase_stats)

    def split_data_speed(self):
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

    def correct_data_speed(self):
        if 1.44 in self.clicks_by_speed.keys():
            base_index = 1.44

        elif round(period_li[default_rotate_ind], 2) in self.clicks_by_speed.keys():
            base_index = round(period_li[default_rotate_ind], 2)

        else:
            raise ValueError("Base rotation speed not in data!")

        base_clicks = self.clicks_by_speed[base_index]
        base_clicks_mean = np.mean(base_clicks)
        # base_clicks = base_clicks - base_clicks_mean
        base_clicks_std = np.std(base_clicks)

        clock_speeds = list(self.clicks_by_speed.keys())
        self.corrected_clicks = []
        for clock_speed in clock_speeds:
            clicks = self.clicks_by_speed[clock_speed]
            clicks_mean = np.mean(clicks)
            clicks = clicks - clicks_mean
            clicks_std = np.std(clicks)
            clicks *= base_clicks_std/clicks_std
            clicks += base_clicks_mean

            self.corrected_clicks += clicks.tolist()

        self.corrected_clicks = np.array(self.corrected_clicks)

    def make_data_frame(self):
        for phrase_num, phrase in enumerate(self.phrases):
            if phrase_num == 0:
                DF = pd.DataFrame(pd.DataFrame([self.phrase_stats[phrase]]))
                DF["phrase"] = phrase
            else:
                df = pd.DataFrame([self.phrase_stats[phrase]])
                df["phrase"] = phrase
                DF = DF.append(df, ignore_index=True)
        # DF = DF.sor _values(by=['start_time'])
        self.DF = DF

    def save_hist(self):
        kernel = stats.gaussian_kde(self.corrected_clicks)
        hist = kernel(np.arange(80))
        PickleUtil(os.path.join(data_dir, "user_histogram.p")).safe_save(kernel)

    def plot_data(self):
        fig = plt.figure()
        ax = plt.subplot(111)
        plot_num = 0
        for clock_speed in self.clicks_by_speed.keys():
            plot_color = self.plot_colors[plot_num]
            clicks = self.clicks_by_speed[clock_speed]
            clicks_mean = np.mean(clicks)
            clicks_std = np.std(clicks)
            # clicks = clicks - clicks_mean

            plot_label = "rotation: "+str(clock_speed)+" ("+str(len(clicks))+" points)"
            # ax.hist(clicks, 30, range=[0, 80], density=True, color=plot_color, alpha=0.3, label=plot_label)

            kernel = stats.gaussian_kde(clicks)
            res = 10
            plt.plot(np.arange(80*res)/res, kernel(np.arange(80*res)/res), color=plot_color, linewidth=2, label=plot_label)
            plot_num += 1

            # plt.axvline(clicks_mean, color=plot_color, linestyle="--", alpha=0.8)
            # for i in [-1,1]:
            #     plt.axvline(clicks_mean + i*clicks_std, color=plot_color, linestyle=":", alpha=0.6)

        if self.corrected_clicks is not None:
            kernel = stats.gaussian_kde(self.corrected_clicks)
            res = 10
            plot_label = "rotation_adj (" + str(len(self.corrected_clicks)) + " points)"
            plt.plot(np.arange(80 * res) / res, kernel(np.arange(80 * res) / res), linestyle="--", color="0000", linewidth=2, label=plot_label)


        # ax.bar(np.arange(self.kde_list.size), self.kde_list, fill=False, edgecolor='black', label="KDE")
        ax.legend()
        # ax.set_xlim(20,60)

        plt.show()

    def plot_phrase_stats(self, DF2=None):

        ind_var_name = "session"
        for data_label in ['error_tot', 'error_tot', 'clicks_char', 'clicks_word', 'clicks_sel', 'words_min',
                           'chars_min', 'sel_min']:

            var_name_dict = {'sel_min': "Selections/Min", 'words_min': "Words/Min", 'chars_min': "Characters/Min",
                             'clicks_char': "Clicks/Character", 'clicks_word': "Clicks/Word",
                             'clicks_sel': "Clicks/Selection", 'error_tot': "Error Rate"}

            dep_var_name = var_name_dict[data_label]

            DF = self.DF
            pd.set_option('display.max_columns', 500)

            fig, ax = plt.subplots()
            fig.set_size_inches(12, 10)
            sns.set(font_scale=1.4, rc={"lines.linewidth": 3})
            sns.set_style({'font.serif': 'Helvetica'})

            if DF2 is not None:
                sns.lineplot(x=ind_var_name, y=data_label, color="rosybrown",
                             data=DF2, ci="sd", ax=ax)

                sns.lineplot(x=ind_var_name, y=data_label, color="brown",
                             data=DF2, ax=ax)

            sns.lineplot(x=ind_var_name, y=data_label, color="cadetblue",
                         data=DF, ci="sd", ax=ax)

            sns.lineplot(x=ind_var_name, y=data_label, color="darkslategrey",
                         data=DF, ax=ax)

            ax.set(xlabel=ind_var_name, ylabel=dep_var_name)

            plt.legend(title='Key:', labels=['Row Col (SD)', '       (95% CI)', 'Nomon (SD)', '     (95% CI)'])

            plt.title("Participant 951: " + dep_var_name + " vs. " + ind_var_name)
            sns.axes_style("darkgrid")
            plt.show()

    def print_stat_avg(self):

        errors = []
        clicks_char = []
        clicks_word = []
        words_min = []
        chars_min = []

        for phrase in self.phrases:
            data_dict = self.phrase_stats[phrase]
            errors.append(data_dict["error_tot"])
            clicks_char.append(data_dict["clicks_char"])
            clicks_word.append(data_dict["clicks_word"])
            words_min.append(data_dict["words_min"])
            chars_min.append(data_dict["chars_min"])
        print("\n")
        print("Characters/Min:   ", np.average(chars_min), "+/-", np.std(chars_min))
        print("Words/Min:        ", np.average(words_min), "+/-", np.std(words_min))
        print("Clicks/Character: ", np.average(clicks_char), "+/-", np.std(clicks_char))
        print("Clicks/Word:      ", np.average(clicks_word), "+/-", np.std(clicks_word))
        print("Error Rate (%):   ", np.average(errors) * 100, "+/-", np.std(errors) * 100)

    def test_significance(self, DF2=None):
        var_name_dict = {'words_min': "Words/Min:        ", 'chars_min': "Characters/Min:   ",
                         'clicks_char': "Clicks/Character: ", 'clicks_word': "Clicks/Word:      ",
                         'error_tot': "Error Rate:       "}

        if DF2 is None:
            df_start = self.DF[self.DF["session"] == 1]
            df_end = self.DF[self.DF["session"] == max(self.DF["session"])]
            print("\n")
            print("Difference in means from first and last session: \n")
            for data_label in ['error_tot', 'clicks_char', 'clicks_word', 'words_min', 'chars_min']:
                sub_data_start = df_start[data_label]
                sub_data_end = df_end[data_label]

                t_val, p_val = stats.ttest_ind(sub_data_start.values, sub_data_end.values,
                                      equal_var=False)

                if p_val > 0.05:
                    print(var_name_dict[data_label] + ": Not statistically significant (p-value: " + str(p_val) + ")")
                else:
                    print(var_name_dict[data_label] + ": Statistically significant     (p-value: " + str(p_val) + ")")

        else:
            df_self = self.DF[self.DF["session"] == max(self.DF["session"])]
            df_other = DF2[DF2["session"] == max(DF2["session"])]
            print("\n")
            print("Difference in means from Nomon and Row Col in last session: \n")
            for data_label in ['error_tot', 'clicks_char', 'clicks_word', 'words_min', 'chars_min']:
                sub_data_self = df_self[data_label]
                sub_data_other = df_other[data_label]

                t_val, p_val = stats.ttest_ind(sub_data_self.values, sub_data_other.values,
                                               equal_var=False)

                if p_val > 0.05:
                    print(var_name_dict[data_label] + ": Not statistically significant (p-value: " + str(p_val) + ")")
                else:
                    print(var_name_dict[data_label] + ": Statistically significant     (p-value: " + str(p_val) + ")")





du = DataUtil(data_dir)
du.load_data()
# du.split_data_speed()
# du.correct_data_speed()
# du.plot_data()
# du.save_hist()
du.split_data_phrase()
du.make_data_frame()

# # du2 = DataUtil(data_dir2)
# # du2.load_data()
# # du2.split_data_phrase()
# # du2.make_data_frame()
#
du.print_stat_avg()
# du.plot_phrase_stats()
# du.test_significance()
