import sys, time, os
import numpy as np
import xarray as xr
sys.path.append(os.path.abspath("/xdisk/sylvia/tropic_vis/utilities/"))
from calc_water import calc_water
   
# Define bins in normalized time
m = 100
tbins_norm = np.linspace( 0., 1., m )

# Load trajectory files
basedir = '/xdisk/sylvia/traj_output/'
clams_fi = xr.open_dataset( basedir + 'CLAMS-Tf_0V2M0A0R_tst00000450_trim_extract_dt_iwc_filter.nc' )
icon_fi = xr.open_dataset( basedir + 'ICON_0V2M0A0R_tst00000450_trim_extract_dt_filter.nc' )

# Which variable?
#icon_traj = icon_fi['qi']
#clams_traj = clams_fi['qi']
#icon_T = icon_fi['T']
#clams_T = clams_fi['T']
#icon_P = icon_fi['p']
#clams_P = clams_fi['PE']
##clams_RHi = clams_fi['RHI']

#icon_traj_ppmv = calc_water( icon_T, icon_P, icon_traj )
#clams_traj_ppmv = calc_water( clams_T, clams_P, clams_traj )

icon_traj0 = icon_fi['Ni'] * icon_fi['rho'] / 1000.
clams_traj0 = clams_fi['Ni'] * clams_fi['rho'] / 1000.
icon_traj = icon_traj0.where( (icon_traj0 > 0) & (clams_traj0 > 0))
clams_traj = clams_traj0.where( (icon_traj0 > 0) & (clams_traj0 > 0))
#clams_RHi = clams_fi['RHI']

del icon_traj
del clams_traj
#del icon_T
#del icon_P
#del clams_T
#del clams_P

# How many trajectories are we handling?
n = clams_fi['id'].shape[0]
diff_vals = np.zeros( (n, m) )
diff_vals[:] = np.nan
vals1 = np.zeros( (n, m) )
vals1[:] = np.nan
vals2 = np.zeros( (n, m) )
vals2[:] = np.nan

# Thresholds as in Postprocessing1.ipynb
RHi_threshold = 0
qi_threshold = 10**(-8)
Ni_threshold = 10**(-8)

c = 0
for j in np.arange(n):
    if (j%100 == 0) & (j != 0):
       print( j )
       np.save( '/xdisk/sylvia/scratch/Ni_ppmv_norm_diff_vals' + str(c) + '_2M.npy', diff_list )
       np.save( '/xdisk/sylvia/scratch/Ni_ppmv_norm_icon_vals' + str(c) + '_2M.npy', val1_list )
       np.save( '/xdisk/sylvia/scratch/Ni_ppmv_norm_clams_vals' + str(c) + '_2M.npy', val2_list )
       c = c + 1

    # Reinitialize this list of differences at every iteration with the bin number <m>
    val1_list = [ [] for i in np.arange(m) ]
    val2_list = [ [] for i in np.arange(m) ]
    diff_list = [ [] for i in np.arange(m) ]
    icon_val = icon_traj_ppmv[:,j]
    clams_val = clams_traj_ppmv[:,j]

    # Apply filters as for the 1D histograms
    icon_val = icon_val.where( (icon_val > qi_threshold) )

    # Find the first and last non-zero element (continuously) along the CLaMS trajectory
    i = np.argwhere( (np.array(clams_val) > qi_threshold) )# & (np.array(clams_RHi[:,j]) > RHi_threshold) )

    # Extract the qi / Ni values in this continuous 'time patch' for both CLaMS and ICON
    # only if such a patch exists
    if len(i) > 3:
       start = i[1][0]
       end = i[-1][0]

       # Calculate the qi / Ni differences along this 'time patch'
       clams_val = clams_val[start:end]
       icon_val = icon_val[start:end]
       diff = icon_val - clams_val

       # Calculate a normalized time coordinate
       #t_norm = np.arange(len(diff))/float(len(diff))
       t_norm = np.arange(len(icon_val))/float(len(icon_val))

       # Digitize these t_norm values into bins
       #k = np.digitize( x=t_norm, bins=tbins_norm )
       k = xr.apply_ufunc( np.digitize, t_norm, tbins_norm )

       for elem_idx, group_idx in enumerate(k):
           val1_list[group_idx].append( icon_val[elem_idx].values )
           val2_list[group_idx].append( clams_val[elem_idx].values )
           diff_list[group_idx].append( diff[elem_idx].values )

       for l in np.arange(m):
           if len(val1_list[l]):
              vals1[j,l] = np.nanmean( val1_list[l] )
           if len(val2_list[l]):
              vals2[j,l] = np.nanmean( val2_list[l] )
           if len(diff_list[l]):
              diff_vals[j,l] = np.nanmean( diff_list[l] )
    else:
       continue


np.save( '/xdisk/sylvia/scratch/Ni_ppmv_norm_diff_vals' + str(c) + '_2M.npy', diff_vals )
np.save( '/xdisk/sylvia/scratch/Ni_ppmv_norm_icon_vals' + str(c) + '_2M.npy', vals1 )
np.save( '/xdisk/sylvia/scratch/Ni_ppmv_norm_clams_vals' + str(c) + '_2M.npy', vals2 )

