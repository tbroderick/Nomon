import os,sys,inspect
import numpy as np
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
os.chdir(parentdir)

from simulated_user import SimulatedUser, normal_hist



job_indicies = np.array_split(np.arange(1, 20), num_tasks)[my_task_id-1]

parameters_list = [{"click_dist": normal_hist(0, i / 2)} for i in job_indicies]
attributes = [i / 2 for i in job_indicies]
for parameters, attribute in zip(parameters_list, attributes):
    sim = SimulatedUser(currentdir)
    sim.parameter_metrics(parameters, num_clicks=200, trials=2, attribute=attribute)
