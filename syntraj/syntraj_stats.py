# Calculate the mean, median, and standard deviation of T, P, qv, qi, qs, theta, RHi
# for a given set of simulation trajs
# This function does not fix the number of elements per bin.
def syntraj_stats( alt_ICON, t_ICON, p_ICON, qv_ICON, qi_ICON, qs_ICON, indx, bins_sim ):

    import numpy as np
    import time, sys, os
    sys.path.append(os.path.abspath("/work/bb1018/b380873/tropic_vis/utilities/"))
    from thermodynamic_functions import *

    n = bins_sim.shape[0]

    # Store 7 variables and 3 statistics over <n> levels for <alt_ICON.shape[1]> trajectories
    stats = np.empty((7, 3, n, alt_ICON.shape[1]))
    stats[:] = np.nan

    for i in np.arange(alt_ICON.shape[1]):
        if i%100 == 0:
           print(i)
        t_list = [ [] for k in np.arange(n) ]
        p_list = [ [] for k in np.arange(n) ]
        qv_list = [ [] for k in np.arange(n) ]
        qi_list = [ [] for k in np.arange(n) ]
        qs_list = [ [] for k in np.arange(n) ]
        theta_list = [ [] for k in np.arange(n) ]
        RHi_list = [ [] for k in np.arange(n) ]

        # Calculate the ICON theta and RHi fields from the T, p, and qv values.
        theta_ICON = calc_theta( t_ICON, p_ICON )
        RHi_ICON = calc_RH( t_ICON, p_ICON, qv_ICON/10**6 )

        # Group values for this trajectory into bins.
        for elem_idx, group_idx in enumerate( indx[:,i] ):
            t_list[int(group_idx)-1].append( t_ICON[elem_idx, i].item() )
            p_list[int(group_idx)-1].append( p_ICON[elem_idx, i].item() )
            qv_list[int(group_idx)-1].append( qv_ICON[elem_idx, i].item() )
            qi_list[int(group_idx)-1].append( qi_ICON[elem_idx, i].item() )
            qs_list[int(group_idx)-1].append( qs_ICON[elem_idx, i].item() )
            theta_list[int(group_idx)-1].append( theta_ICON[elem_idx,i].item() )
            RHi_list[int(group_idx)-1].append( RHi_ICON[elem_idx,i].item() )

        for j in np.arange(n):
            stats[0, 0, j, i] = np.nanmean( t_list[j] )
            stats[0, 1, j, i] = np.nanmedian( t_list[j] )
            stats[0, 2, j, i] = np.nanstd( t_list[j] )

            stats[1, 0, j, i] = np.nanmean( p_list[j] )
            stats[1, 1, j, i] = np.nanmedian( p_list[j] )
            stats[1, 2, j, i] = np.nanstd( p_list[j] )

            stats[2, 0, j, i] = np.nanmean( qv_list[j] )
            stats[2, 1, j, i] = np.nanmedian( qv_list[j] )
            stats[2, 2, j, i] = np.nanstd( qv_list[j] )

            stats[3, 0, j, i] = np.nanmean( qi_list[j] )
            stats[3, 1, j, i] = np.nanmedian( qi_list[j] )
            stats[3, 2, j, i] = np.nanstd( qi_list[j] )

            stats[4, 0, j, i] = np.nanmean( qs_list[j] )
            stats[4, 1, j, i] = np.nanmedian( qs_list[j] )
            stats[4, 2, j, i] = np.nanstd( qs_list[j] )

            stats[5, 0, j, i] = np.nanmean( theta_list[j] )
            stats[5, 1, j, i] = np.nanmedian( theta_list[j] )
            stats[5, 2, j, i] = np.nanstd( theta_list[j] )

            stats[6, 0, j, i] = np.nanmean( RHi_list[j] )
            stats[6, 1, j, i] = np.nanmedian( RHi_list[j] )
            stats[6, 2, j, i] = np.nanstd( RHi_list[j] )

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return stats
