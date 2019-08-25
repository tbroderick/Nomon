#!/bin/sh

#SBATCH -o sim_rotation_speed.out-%j-%a
#SBATCH -a 1-20

# run with: sbatch jobArray.sh
# or run with: LLsub jobArray.sh

# Initialize Modules
source /etc/profile

# Load Julia Module
module load anaconda3-5.0.1

echo "My SLURM_ARRAY_TASK_ID: " $SLURM_ARRAY_TASK_ID
echo "Number of Tasks: " $SLURM_ARRAY_TASK_COUNT

python3 rotation_speed.py $SLURM_ARRAY_TASK_ID $SLURM_ARRAY_TASK_COUNT

