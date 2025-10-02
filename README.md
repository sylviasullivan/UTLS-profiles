flight1 - Directory of additional run scripts to complete ICON simulations for different sets of ice microphysics and optics

syntraj - Directory of functions to 1) create synthetic trajectories from ICON simulation output (collocateFunc.py, extractFunc.py, syntrajDriver.py), 2) evaluate statistics of those synthetic trajectories (statisticsDriver.py, statisticsFunc.py), and 3) submit those functions as batch jobs (submit_syntraj.sh)

traj - Directory of functions to handle the online ICON trajectories. For the UTLS study, we use traj_psd.py to create power spectra of temperature and vertical velocity along these. Other functions are not used.

utilities - Directory of utility functions to 1) apply MLS averaging kernels (mls_regrid_kernel.py), 2) generates plots (plotting_utilities.py), and 3) calculate thermodynamic values such as the saturation vapor mixing ratio (thermodynamic_functions.py).

\*M\*O_flight\*_update.run -- Run scripts to complete ICON simulations for different sets of ice microphysics and optics

Analysis\_article3.ipynb -- Jupyter notebook to evaluate statistics and values cited throughout the UTLS study

CLCONV_WINDTH_merge.sh -- Script to merge simulation output files with cloud/convective fields (CLCONV) and wind/thermodynamic fields (WINDTH)

Figures\_article3.ipynb -- Jupyter notebook to reproduce all figures in the UTLS study

SI\_article3.ipynb -- Jupyter notebook with supplementary visualizations for the UTLS study
