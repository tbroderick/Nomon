import os
from pickle_util import PickleUtil
from matplotlib import pyplot as plt
from scipy import stats
from config import period_li, default_rotate_ind
from phrases import Phrases
from text_stats import calc_MSD
import numpy as np

data_dir = "C:\\Users\\nickb\\AppData\\Local\\Nomon\data\\2"


def flatten(l):
    return [item for sublist in l for item in sublist]


class DataUtil:
    def __init__(self, data_dir):
        self.phrase_util = Phrases("resources/comm2.dev")
        self.plot_colors = ["#0000ff", "#00aa00", "#aa0000", "#ff7700", "#aa00aa"]
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

        for selection_num, selection in enumerate(self.selection_data):  # scan through data to find phrases & time ints
            phrase = selection["target"]
            typed = selection["typed"]
            is_backspace = selection["backspace"]
            is_undo = selection["undo"]

            if phrase not in self.phrases:
                self.phrases.append(phrase)
                phrase_start = selection["time"]

            if is_backspace:  # accumulate corrected errors
                corrected_error += 1
            if is_undo:
                if selection_num > 0:
                    prev_typed = self.selection_data[selection_num-1]["typed"]
                    typed_difference = prev_typed[len(typed):]
                    corrected_error += len(typed_difference)

            _, completed_phrase = self.phrase_util.compare(typed, phrase)
            if completed_phrase:
                self.phrase_times[phrase] = (phrase_start, selection["time"])
                uncorrected_error = calc_MSD(typed, phrase)[0]
                total_error = (uncorrected_error + corrected_error) / len(max(typed, phrase))

                self.phrase_stats[phrase] = {"error_unc": uncorrected_error, "error_cor": corrected_error,
                                             "error_tot": total_error}

                uncorrected_error = 0
                corrected_error = 0

        for phrase in self.phrases:  # remove incomplete phrases
            if phrase not in self.phrase_times:
                self.phrases.remove(phrase)

        print("Data partitioned into " + str(len(self.phrases)) + " sets by phrase")

        for phrase in self.phrases:  # split data according to phrase times calculated above
            phrase_start, phrase_end = self.phrase_times[phrase]
            phrase_click_indices = np.where((self.abs_click_data >= phrase_start) & (self.abs_click_data <= phrase_end))
            phrase_abs_clicks = self.abs_click_data[phrase_click_indices]
            phrase_rel_clicks = self.rel_click_data[phrase_click_indices]

            self.clicks_by_phrase[phrase] = {"abs": phrase_abs_clicks, "rel": phrase_rel_clicks}

            num_clicks = len(phrase_abs_clicks)
            time_int = phrase_end - phrase_start
            num_characters = len(phrase)
            num_words = len(phrase.split(" "))

            clicks_per_char = num_clicks / num_characters
            clicks_per_word = num_clicks / num_words
            chars_per_min = num_characters / time_int * 60
            words_per_min = num_words / time_int * 60

            stat_dict = self.phrase_stats[phrase]
            stat_dict["clicks_char"] = clicks_per_char
            stat_dict["clicks_word"] = clicks_per_word
            stat_dict["chars_min"] = chars_per_min
            stat_dict["words_min"] = words_per_min

        print(self.phrase_stats)

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

    def save_hist(self):
        kernel = stats.gaussian_kde(self.corrected_clicks)
        hist = kernel(np.arange(80))
        PickleUtil(os.path.join(data_dir, "user_histogram.p")).safe_save(hist)

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
            ax.hist(clicks, 30, range=[0, 80], density=True, color=plot_color, alpha=0.3, label=plot_label)

            kernel = stats.gaussian_kde(clicks)
            res = 10
            plt.plot(np.arange(80*res)/res, kernel(np.arange(80*res)/res), color=plot_color, linewidth=2)
            plot_num += 1

            plt.axvline(clicks_mean, color=plot_color, linestyle="--", alpha=0.8)
            for i in [-1,1]:
                plt.axvline(clicks_mean + i*clicks_std, color=plot_color, linestyle=":", alpha=0.6)

        if self.corrected_clicks is not None:
            kernel = stats.gaussian_kde(self.corrected_clicks)
            res = 10
            plot_color = self.plot_colors[plot_num]
            plot_label = "rotation_adj (" + str(len(self.corrected_clicks)) + " points)"
            plt.plot(np.arange(80 * res) / res, kernel(np.arange(80 * res) / res), linestyle="--", color="0000", linewidth=2, label=plot_label)


        # ax.bar(np.arange(self.kde_list.size), self.kde_list, fill=False, edgecolor='black', label="KDE")
        ax.legend()
        # ax.set_xlim(20,60)

        plt.show()

    def plot_stat_data(self):

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

        plt.plot(chars_min)
        plt.ylabel("Characters per Min")
        plt.xlabel("Phrase Number")
        plt.title("Characters per Min by Phrase")
        plt.show()


du = DataUtil(data_dir)
du.load_data()
du.split_data_speed()
du.split_data_phrase()
# du.correct_data()
# du.save_hist()
du.plot_stat_data()