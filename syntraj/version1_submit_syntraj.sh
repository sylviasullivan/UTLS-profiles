#!/bin/sh
#SBATCH --account=sylvia
#SBATCH --job-name=syntraj
#SBATCH --partition=high_priority
#SBATCH --cores=2
#SBATCH --mem=200gb
#SBATCH --nodes=4
#SBATCH --qos=user_qos_sylvia
#SBATCH --output=/groups/sylvia/UTLS-profiles/syntraj/LOG_syntraj.%j.o
#SBATCH --error=/groups/sylvia/UTLS-profiles/syntraj/LOG_syntraj.%j.o
#SBATCH --time=01:00:00

#source activate ncplot
python extractme.py
