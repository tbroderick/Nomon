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
    my_task_id = 1
    num_tasks = 2


parameters_list = []
click_dists = [PickleUtil(os.path.join("simulations/param_opt/click_distributions", file)).safe_load() for file in os.listdir("simulations/param_opt/click_distributions")]

for click_dist in click_dists:
    for left_context in [True, False]:
        click_dist = click_dist/np.sum(click_dist)
        param_dict = dict()
        param_dict["click_dist"] = click_dist.tolist()
        param_dict["N_pred"] = 3
        param_dict["num_words"] = 17
        param_dict["left_context"] = left_context
        parameters_list += [param_dict.copy()]

print(len(parameters_list))
num_jobs = len(parameters_list)
job_indices = np.array_split(np.arange(1, num_jobs + 1), num_tasks)[my_task_id - 1]
print(job_indices)

for job_index in job_indices:
    parameters = parameters_list[job_index-1]
    user_num = int((job_index*len(click_dists)*0.999)/num_jobs)
    print(user_num)
    sim = SimulatedUser(currentdir, job_num=user_num)
    sim.parameter_metrics(parameters, num_clicks=750, trials=50)
