#!/bin/sh
#SBATCH --account=sylvia
#SBATCH --job-name=E2_all
#SBATCH --partition=high_priority
#SBATCH --cores=2
#SBATCH --mem=200gb
#SBATCH --nodes=4
#SBATCH --qos=user_qos_sylvia
#SBATCH --output=/groups/sylvia/UTLS-profiles/syntraj/LOG_collocate.%j.o
#SBATCH --error=/groups/sylvia/UTLS-profiles/syntraj/LOG_collocate.%j.o
#SBATCH --time=08:00:00

# Extract subset
python syntrajDriver.py 1M0O E2
python statisticsDriver.py 1M0O E2
python syntrajDriver.py 1M1O E2
python statisticsDriver.py 1M1O E2
python syntrajDriver.py 1M3O E2
python statisticsDriver.py 1M3O E2
python syntrajDriver.py 2M0O E2
python statisticsDriver.py 2M0O E2
python syntrajDriver.py 2M1O E2
python statisticsDriver.py 2M1O E2
python syntrajDriver.py 2M3O E2
python statisticsDriver.py 2M3O E2

# Collocate subset
#python syntrajDriver.py 1M0O C
#python statisticsDriver.py 1M0O C
#python syntrajDriver.py 1M1O C
#python statisticsDriver.py 1M1O C
#python syntrajDriver.py 1M3O C
#python statisticsDriver.py 1M3O C

#python syntrajDriver.py 2M0O C
#python statisticsDriver.py 2M0O C
#python syntrajDriver.py 2M1O C
#python statisticsDriver.py 2M1O C
#python syntrajDriver.py 2M3O C
#python statisticsDriver.py 2M3O C
