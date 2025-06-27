#!/bin/sh
#SBATCH --account=sylvia
#SBATCH --job-name=E1M1O
#SBATCH --partition=high_priority
#SBATCH --cores=2
#SBATCH --mem=200gb
#SBATCH --nodes=4
#SBATCH --qos=user_qos_sylvia
#SBATCH --output=/groups/sylvia/UTLS-profiles/syntraj/LOG_extract.%j.o
#SBATCH --error=/groups/sylvia/UTLS-profiles/syntraj/LOG_extract.%j.o
#SBATCH --time=01:00:00

#python extractDriver.py 2M1O
python statisticsDriver.py 1M0O E

#python extractDriver.py 2M3O
#python statisticsDriver.py 2M3O E
