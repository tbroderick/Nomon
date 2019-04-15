import os
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

    def plot_across_user(self, metric, params=None):
        dep_vars = []
        ind_vars = []
        for user in self.user_numbers:
            user_data = self.data_by_user[user]

            if params is None:
                params = list(user_data.keys())[1]
            else:
                if params not in user_data.keys():
                    raise KeyError("Parameters are not in saved data")

            if metric not in user_data[params].keys():
                raise KeyError("Metric is not in saved data")

            dep_vars += [user_data[params][metric]]
            if "attribute" in user_data[params]:
                ind_vars += [user_data[params]["attribute"]]
            else:
                ind_vars += [user]

        data_points = list(zip(ind_vars, dep_vars))
        data_points.sort()
        ind_vars, dep_vars = zip(*data_points)

        if np.array(dep_vars[0]).size == 1:
            plt.plot(ind_vars, dep_vars)
            plt.show()

        # else:
        #     for


def main():
    sdu = SimDataUtil("simulations/increasing_variance/sim_data")
    sdu.plot_across_user("selections", (3, 0.008))
    sdu.plot_across_user("presses", (3, 0.008))
    sdu.plot_across_user("kde_mses", (3, 0.008))


if __name__ == '__main__':
    main()
