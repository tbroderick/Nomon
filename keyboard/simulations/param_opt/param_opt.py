import os,sys,inspect
import numpy as np
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
os.chdir(parentdir)

from simulated_user import SimulatedUser, normal_hist
from pickle_util import PickleUtil

try:
    my_task_id = int(sys.argv[1])
    num_tasks = int(sys.argv[2])
except IndexError:
    my_task_id = 24
    num_tasks = 24


class simulationUtil():
    def __init__(self):
        print(os.listdir("simulations/param_opt/click_distributions"))
        self.click_dists = [PickleUtil(os.path.join("simulations/param_opt/click_distributions", file)).safe_load() for
                            file in os.listdir("simulations/param_opt/click_distributions")]
        self.dp_dists = [PickleUtil(os.path.join("simulations/param_opt/dp_distributions", file)).safe_load() for
                            file in os.listdir("simulations/param_opt/dp_distributions")]
        self.n_pred_range = [3]

        self.parameters_list = []

    def run_job(self, my_task_id, num_tasks, num_clicks=1000, trials=10):

        for click_dist, dp_dist in zip(self.click_dists, self.dp_dists):
            # click_dist = click_dist / np.sum(click_dist)
            param_dict = {}
            param_dict["click_dist"] = click_dist
            param_dict["dp_dist"] = dp_dist
            param_dict["time_rotate"] = 4
            for n_pred in self.n_pred_range:
                param_dict["N_pred"] = n_pred
                for num_words in range(0, n_pred * 26, 3):
                    param_dict["num_words"] = num_words
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

# for job_index in job_indicies:
#     parameters = parameters_list[job_index-1]
#     user_num = int((job_index*len(click_dists)*0.999)/num_jobs)
#     print(user_num)
#     sim = SimulatedUser(currentdir, job_num=user_num)
#
#     sim.parameter_metrics(parameters, num_clicks=500, trials=30)
