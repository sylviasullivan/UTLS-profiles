import numpy as np
import xarray as xr
from datetime import datetime
from syntraj_stats_fixed import syntraj_stats_fixed

# Binning values - These come from the in-situ data but we have fewer model levels.
#u = 14000
#d = 22000
#n = 70

# Binning values from the vertical grid file
vgrid = xr.open_dataset('/work/bb1018/b380873/vgrid_icon-grid_tropic_55e115e5s40n.nc')
alt = vgrid.vct_a.values[:,0]
j = np.argwhere((alt >= 14000) & (alt <= 22000))
bins_sims = alt[j[:,0]]

# Time range from Lee et al. 2019 (6:20-6:48 UTC)
time0 = datetime(2017, 8, 8, 6, 20)
timef = datetime(2017, 8, 8, 6, 48)

# Do the same for the synthetic simulation trajectories
basedir = '/work/bb1018/b380873/model_output/ICON/'
tag = ''  # Default 625 synthetic trajectories
#tag = '_fixed' # Fix the number of elements per bin to that of the in-situ measurements
#tag = '_2' # Second set of 625 synthetic trajectories to test reproducibility
#tag = '_collocate' # Minimize the Euclidean distance between sim and obs values
#tag = '_pinpoint' # Find the closest numerical value to the obs within the sim

syntraj1 = xr.open_dataset(basedir + 'ICON_synthetic_trajs_0V1M0A0R' + tag + '.nc')
syntraj2 = xr.open_dataset(basedir + 'ICON_synthetic_trajs_0V2M0A0R' + tag + '.nc')
syntraj3 = xr.open_dataset(basedir + 'ICON_synthetic_trajs_0V2M1A1R' + tag + '.nc')

alt_ICON1 = syntraj1['alt'].sel( time=slice(time0, timef) )
temp_ICON1 = syntraj1['temp'].sel( time=slice(time0, timef) )
press_ICON1 = syntraj1['air_pressure'].sel( time=slice(time0, timef) )

alt_ICON2 = syntraj2['alt'].sel( time=slice(time0, timef) )
temp_ICON2 = syntraj2['temp'].sel( time=slice(time0, timef) )
press_ICON2 = syntraj2['air_pressure'].sel( time=slice(time0, timef) )

alt_ICON3 = syntraj3['alt'].sel( time=slice(time0, timef) )
temp_ICON3 = syntraj3['temp'].sel( time=slice(time0, timef) )
press_ICON3 = syntraj3['air_pressure'].sel( time=slice(time0, timef) )

# Convert kg kg-1 to ppmv for the mixing ratios
mw_dryair = 28.97*1000    # kg air (mol air)-1
mw_watvap = 18.02*1000    # kg wv (mol wv)-1
conv = mw_dryair / mw_watvap

qv_ICON1 = syntraj1['qv'].sel( time=slice(time0, timef) ) * conv * 10**6
qv_ICON2 = syntraj2['qv'].sel( time=slice(time0, timef) ) * conv * 10**6
qv_ICON3 = syntraj3['qv'].sel( time=slice(time0, timef) ) * conv * 10**6

qi_ICON1 = syntraj1['qi'].sel( time=slice(time0, timef) ) * conv * 10**6
qi_ICON2 = syntraj2['qi'].sel( time=slice(time0, timef) ) * conv * 10**6
qi_ICON3 = syntraj3['qi'].sel( time=slice(time0, timef) ) * conv * 10**6

qs_ICON1 = syntraj1['qs'].sel( time=slice(time0, timef) ) * conv * 10**6
qs_ICON2 = syntraj2['qs'].sel( time=slice(time0, timef) ) * conv * 10**6
qs_ICON3 = syntraj3['qs'].sel( time=slice(time0, timef) ) * conv * 10**6

# Binning in altitude between <u> and <d> with <n> bins, which elements go in which bin?
# np.digitize returns the indices of the bins to which each element in alt* belongs.
# 3 sets of simulations, 1681 times, 625 trajectories
idx = np.zeros((3, alt_ICON1.shape[0], alt_ICON1.shape[1]))
for i in np.arange(alt_ICON1.shape[1]):
    idx[0,:,i] = np.digitize( alt_ICON1[:,i], bins=bins_sims )
    idx[1,:,i] = np.digitize( alt_ICON2[:,i], bins=bins_sims )
    idx[2,:,i] = np.digitize( alt_ICON3[:,i], bins=bins_sims )
    #idx[0,:,i] = np.digitize( alt_ICON1[:,i], bins=np.linspace(u,d,n) )
    #idx[1,:,i] = np.digitize( alt_ICON2[:,i], bins=np.linspace(u,d,n) )
    #idx[2,:,i] = np.digitize( alt_ICON3[:,i], bins=np.linspace(u,d,n) )

stats1_fixed = syntraj_stats_fixed( alt_ICON1, temp_ICON1, press_ICON1, qv_ICON1, qi_ICON1, qs_ICON1, idx[0], bins_sims )
np.save('../../output/ICON_syntrajs_0V1M0A0R_stats' + tag + '_fixed.npy', stats1_fixed)
stats2_fixed = syntraj_stats_fixed( alt_ICON2, temp_ICON2, press_ICON2, qv_ICON2, qi_ICON2, qs_ICON2, idx[1], bins_sims )
np.save('../../output/ICON_syntrajs_0V2M0A0R_stats' + tag + '_fixed.npy', stats2_fixed)
stats3_fixed = syntraj_stats_fixed( alt_ICON3, temp_ICON3, press_ICON3, qv_ICON3, qi_ICON3, qs_ICON3, idx[2], bins_sims )
np.save('../../output/ICON_syntrajs_0V2M1A1R_stats' + tag + '_fixed.npy', stats3_fixed)
