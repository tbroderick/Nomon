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


parameters_list = []
click_dists = [PickleUtil(os.path.join("simulations/param_opt/click_distributions", file)).safe_load() for file in os.listdir("simulations/param_opt/click_distributions")]

n_pred_range = np.arange(1, 4, 1).tolist()

for click_dist in click_dists:
    if isinstance(click_dist, dict):
        click_dist = np.array(click_dist["li"])
    click_dist = click_dist/np.sum(click_dist)
    param_dict = {}
    param_dict["click_dist"] = click_dist.tolist()
    for n_pred in n_pred_range:
        param_dict["N_pred"] = n_pred
        for num_words in range(0, n_pred * 26, 3):
            param_dict["num_words"] = num_words
            parameters_list += [param_dict.copy()]

print(len(parameters_list))
num_jobs = len(parameters_list)
job_indicies = np.array_split(np.arange(1, num_jobs+1), num_tasks)[my_task_id-1]
print(job_indicies)

for job_index in job_indicies:
    parameters = parameters_list[job_index-1]
    user_num = int((job_index*len(click_dists)*0.999)/num_jobs)
    print(user_num)
    sim = SimulatedUser(currentdir, job_num=user_num)

    sim.parameter_metrics(parameters, num_clicks=500, trials=30)
