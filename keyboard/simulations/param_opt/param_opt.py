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
    my_task_id = 9
    num_tasks = 20


parameters_list = []
click_dists = [PickleUtil(os.path.join("simulations/param_opt/click_distributions", file)).safe_load() for file in os.listdir("simulations/param_opt/click_distributions")]

prob_thresh_range = np.arange(0,0.02,0.001).tolist()
n_pred_range = np.arange(1, 4, 1).tolist()

for click_dist in click_dists:
    click_dist = click_dist/np.sum(click_dist)
    param_dict = {}
    param_dict["click_dist"] = click_dist.tolist()
    for n_pred in n_pred_range:
        param_dict["N_pred"] = n_pred
        for prob_thresh in prob_thresh_range:
            param_dict["prob_thresh"] = prob_thresh
            parameters_list += [param_dict.copy()]

print(len(parameters_list))
num_jobs = len(parameters_list)
job_indicies = np.array_split(np.arange(1, num_jobs+1), num_tasks)[my_task_id-1]
print(job_indicies)

for job_index in job_indicies:
    parameters = parameters_list[job_index-1]
    sim = SimulatedUser(currentdir)
    sim.parameter_metrics(parameters, num_clicks=750, trials=40)
