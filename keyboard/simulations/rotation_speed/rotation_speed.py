import os,sys,inspect
import numpy as np
from scipy import stats
# from matplotlib import pyplot as plt
import multiprocessing as mp
import time


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
parentdir = os.path.dirname(parentdir)
os.chdir(parentdir)
sys.path.append(parentdir)

from simulated_user import SimulatedUser
from pickle_util import PickleUtil

try:
    my_task_id = int(sys.argv[1])
    num_tasks = int(sys.argv[2])
except IndexError:
    my_task_id = 1
    num_tasks = 8


class simulationUtil():
    def __init__(self):
        self.click_dists = [PickleUtil(os.path.join("simulations/rotation_speed/click_distributions", file)).safe_load()
                       for file in os.listdir("simulations/rotation_speed/click_distributions")]

        self.period_li = np.arange(0, 21, 1)

        self.parameters_list = []

    def run_job(self, my_task_id, num_tasks, num_clicks=1500, trials=20):

        for period_num in self.period_li:
            param_dict = dict()
            param_dict["time_rotate"] = period_num
            param_dict["N_pred"] = 3
            param_dict["num_words"] = 17

            for dist in self.click_dists:
                hist = dist(np.arange(80))
                hist = hist / np.sum(hist)
                param_dict["click_dist"] = hist.tolist()

                self.parameters_list += [param_dict.copy()]

        print(len(self.parameters_list))
        num_jobs = len(self.parameters_list)
        job_indicies = np.array_split(np.arange(1, num_jobs+1), num_tasks)[my_task_id-1]
        print(job_indicies)

        for job_index in job_indicies:
            parameters = self.parameters_list[job_index-1]
            user_num = int((job_index*0.999)/num_jobs)
            print(user_num)
            sim = SimulatedUser(parentdir, job_num=user_num)
            sim.parameter_metrics(parameters, num_clicks=num_clicks, trials=trials)


if __name__ == '__main__':
    sim_util = simulationUtil()
    sim_util.run_job(my_task_id, num_tasks)