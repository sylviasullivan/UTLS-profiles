#!/bin/ksh
#SBATCH --account=bb1018
#SBATCH --job-name=stat_fixed
#SBATCH --partition=compute
#SBATCH --mem=10gb
#SBATCH --nodes=1
#SBATCH --output=/work/bb1018/b380873/tropic_vis/traj/syntraj/LOG_syntraj_stat.%j.o
#SBATCH --error=/work/bb1018/b380873/tropic_vis/traj/syntraj/LOG_syntraj_stat.%j.o
#SBATCH --time=08:00:00

#python statme.py
python statme_fixed.py
