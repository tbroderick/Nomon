######################################
#    Copyright 2009 Tamara Broderick
#    This file is part of Nomon Keyboard.
#
#    Nomon Keyboard is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Nomon Keyboard is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Nomon Keyboard.  If not, see <http://www.gnu.org/licenses/>.
######################################


import multiprocessing as mp
import time
import numpy as np

from simulations.param_opt.param_opt import simulationUtil


def submission_fun(task_id):
    sim_util = simulationUtil()
    result = sim_util.run_job(task_id, 3, num_clicks=500, trials=1)
    return result


def main():

    pool = mp.Pool(3)
    result = pool.map(submission_fun, range(1, 4, 1))


if __name__ == "__main__":
    main()