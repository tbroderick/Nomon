import os
from shutil import copyfile
from pickle_util import PickleUtil
from matplotlib import pyplot as plt
from scipy import stats
import numpy as np


class SimDataUtil:

    def __init__(self, data_dir):
        self.data_directory = data_dir
        self.data_by_user = self.load_data()
        self.user_numbers = set(self.data_by_user.keys())

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
                            params = [p.split("_pthres_") for p in params][1]
                            params = [p for sublist in params for p in sublist.split(".p")][:2]
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

    def plot_across_params(self):
        average_data = {}
        num_users = len(self.user_numbers)
        for user in self.user_numbers:
            user_data = self.data_by_user[user]
            for param in user_data:
                if param != "click_dist":
                    if param not in average_data:
                        average_data[param] = {'errors': 0, 'selections': 0, 'characters': 0, 'presses': 0}
                    for data_label in ['errors', 'selections', 'characters', 'presses']:
                        average_data[param][data_label] += user_data[param][data_label] / num_users

        N_preds = list(set([param[0] for param in average_data]))
        N_preds.sort()
        prob_threshs = list(set([param[1] for param in average_data]))
        prob_threshs.sort()

        for data_label in ['errors', 'selections', 'characters', 'presses']:
            plot_values = np.zeros(len(prob_threshs))
            plot_values_2 = np.zeros(len(prob_threshs))
            colors = ["C0", "C1", "C2"]
            ci=0
            for y_index, N_pred in enumerate(N_preds):
                for x_index, prob_thresh in enumerate(prob_threshs):
                    plot_values[x_index] = average_data[(N_pred, prob_thresh)][data_label]
                    plot_values_2[x_index] = average_data[(N_pred, prob_thresh)]["selections"]
                plt.plot(plot_values_2, plot_values, color=colors[ci], label="N Pred = "+str(N_pred))
                plt.plot(plot_values_2[0], plot_values[0], '-o', color=colors[ci], markersize=7)
                plt.plot(plot_values_2[-1], plot_values[-1], '-s', color=colors[ci], markersize=7)
                ci += 1
            plt.legend()
            plt.xlabel("selections per minute")
            if data_label in ['selections', 'characters']:
                plt.ylabel(data_label+str(" per minute"))
            else:
                plt.ylabel(data_label + str(" per selection"))

            plt.title(data_label + " vs selections")
            plt.show()

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
                    os.mkdir(os.path.join(dir, os.path.join("ordered_data", str(click_dists.index(click_dist)))))

            if "npred" in file:
                new_dir = os.path.join(dir, os.path.join("ordered_data", str(click_dists.index(click_dist))))
                if not os.path.exists(os.path.join(new_dir, file)):
                    copyfile(os.path.join(path, file), os.path.join(new_dir, file))
                else:
                    new_dir = os.path.join(dir, os.path.join("ordered_data", str(len(click_dists))))
                    if not os.path.exists(new_dir):
                        os.mkdir(new_dir)
                    copyfile(os.path.join(path, file), os.path.join(new_dir, file))


def main():
    # sdu = SimDataUtil("simulations/increasing_variance/supercloud_results")
    # plot_legend = {"title": "MSE Improvement of Nomon KDE vs Click Distribution Variance", "x": "Standard Deviation (# hist bins)",
    #                "y": "Average (-) Gradient of MSE Over Presses"}
    # sdu.plot_across_user("kde_mses", (3, 0.008), trends=True, log=False, legend=plot_legend)

    # order_data("simulations/param_opt/supercloud_results")

    sdu = SimDataUtil("simulations/param_opt/sim_data")
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
