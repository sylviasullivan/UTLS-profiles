#!/bin/bash
#SBATCH --account=sylvia
#SBATCH --job-name=qia_1M
#SBATCH --partition=high_priority
#SBATCH --qos=user_qos_sylvia
#SBATCH --mem=50gb
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --output=/xdisk/sylvia/tropic_vis/traj/LOG_qi_abs_1M.%j.o
#SBATCH --error=/xdisk/sylvia/tropic_vis/traj/LOG_qi_abs_1M.%j.o
#SBATCH --time=08:00:00

module load anaconda/2020
source ~/.bashrc
conda activate ncplot
#python diff_norm_lifetime.py
python diff_abs_lifetime.py
