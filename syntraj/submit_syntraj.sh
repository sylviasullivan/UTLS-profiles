#!/bin/ksh
#SBATCH --account=bb1018
#SBATCH --job-name=syntraj
#SBATCH --partition=compute2
#SBATCH --mem=20gb
#SBATCH --nodes=1
#SBATCH --output=/work/bb1018/b380873/tropic_vis/traj/syntraj/LOG_syntraj.%j.o
#SBATCH --error=/work/bb1018/b380873/tropic_vis/traj/syntraj/LOG_syntraj.%j.o
#SBATCH --time=02:30:00

#source activate ncplot
python extractme.py
