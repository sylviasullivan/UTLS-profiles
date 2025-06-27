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

# Create bins for ICON synthetic trajectories from the vertical grid file
vgrid = xr.open_dataset('/xdisk/sylvia/vgrid_icon-grid_tropic_55e115e5s40n.nc')
alt = vgrid.vct_a.values[:,0]
j = np.argwhere( (alt >= 5000) & (alt <= 22000) )
bins_sims = alt[ j[:,0] ]
print( 'Total vertical bins to be used: ' + str(len(bins_sims)) )

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
stats = statisticsFunc( ds_current, bins_sims )
stats.to_netcdf( bd + 'ICON_synthetic_trajs_stats_' + s + '_' + tag + '.nc' )
