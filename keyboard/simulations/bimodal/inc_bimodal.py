import os,sys,inspect
import numpy as np
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
os.chdir(parentdir)

from simulated_user import SimulatedUser, normal_hist
from matplotlib import pyplot as plt

try:
    my_task_id = int(sys.argv[1])
    num_tasks = int(sys.argv[2])
except IndexError:
    my_task_id = 2
    num_tasks = 10

jobs = np.arange(1,21)
first_half, second_half = np.array_split(jobs, 2)
weaved_jobs = np.empty((first_half.size + second_half.size,), dtype=first_half.dtype)
weaved_jobs[0::2] = first_half
weaved_jobs[1::2] = second_half[::-1]

job_indicies = np.array_split(weaved_jobs, num_tasks)[my_task_id]

parameters_list = [{"click_dist": (normal_hist(0, 2)+normal_hist(0+i*2, 2))/2} for i in job_indicies]
for par in parameters_list:
    plt.bar(np.arange(80), par["click_dist"])
    plt.show()
# print(len(parameters_list))
attributes = [i*2 for i in job_indicies]
for parameters, attribute in zip(parameters_list, attributes):
    sim = SimulatedUser(currentdir)
    sim.parameter_metrics(parameters, num_clicks=200, trials=10, attribute=attribute)
