import sys
import numpy as np
import xarray as xr
from datetime import datetime
from statisticsFunc import statisticsFunc

# Run this driver like python statisticsDriver.py <sim_acronym> <syntraj_tag> (e.g., python statisticsDriver.py 1M0O E)
s = sys.argv[1]
tag = sys.argv[2]  
# 'E' for extract - Take 20 random simulated values around the in-situ observation
# 'C' for collocate - Minimize the Euclidean distance between sim and obs values
# 'P' for pinpoint - Find the closest numerical value to the obs within the sim
# '_fixed' - Fix the number of elements per bin to that of the in-situ measurements
# '_2' - Second set of randomly sampled synthetic trajectories to test reproducibility
# '_3' # Third set of randomly sampled synthetic trajectories to test reproducibility

# Discrete pressure levels from ICON simulation for binning
file = xr.open_dataset( '/xdisk/sylvia/UTLS_flight_output/1M0O/ICON_3D_flight_1M0O.nc' )
plevs = file.plev.values
print( 'Total pressure bins to be used: ' + str(len(plevs)) )

# Time range from Lee et al. 2019 (6:20-6:48 UTC)
#time0 = datetime(2017, 8, 8, 6, 20)
#timef = datetime(2017, 8, 8, 6, 48)
time0 = datetime(2017, 8, 8, 4, 0)
timef = datetime(2017, 8, 8, 7, 15)

# Define tags and base directory for the various ICON synthetic trajectories
bd = '/groups/sylvia/UTLS-profiles/output/'
st = xr.open_dataset(bd + 'ICON_synthetic_trajs_' + s + '_' + tag + '.nc')
ds_current = st.sel( time=slice(time0, timef) )

# Evaluate the statistics on ds_current and save
stats = statisticsFunc( ds_current, plevs )
stats.to_netcdf( bd + 'ICON_synthetic_trajs_stats_' + s + '_' + tag + '.nc' )
