# Generate a 2-d density plot
# datasets are postprocessed 2D histogram values
# raw are the non-postprocessed traj output to extract ellipses
# histvals is 'qiTh', 'qiRHih', 'NiTh_flight', 'NiRHih_instiu', etc
# xvar is the variable along the x-axis ('T' or 'RHi') and xmin / xmax are its bounds
# yvar is the variable along the y-axis ('qi' or 'Ni')
# tiwc_line is an optional boolean to include the in-situ climatological T-IWC line of Kraemer et al
# centroid is an optional boolean to include the centroid of the density plot
# figsave is an optional boolean to save the output plot to a pdf

def densityPlot( datasets, raw, histvals, xvar, xmin, xmax, yvar, tiwc_line=False,
                    centroid=False, figsave=False ):
    import xarray as xr
    import matplotlib.pyplot as plt
    import sys, os
    import numpy as np
    from matplotlib import cm, colors
    from plotting_utilities import sexy_axes
    sys.path.append(os.path.abspath("/xdisk/sylvia/tropic_vis/traj/"))
    sys.path.append(os.path.abspath("/xdisk/sylvia/tropic_vis/utilities/"))
    from icetraj import martina_T_IWC_line, martina_T_qi_perc_tropics
    #from matplotlib.patches import Ellipse
    from plotting_utilities import stdev_bubble

    fs = 15
    ymin = -3
    ymax = 3.5
    alf = 0.5
    # 20220810_sylvia I believe that these values were calculated within utilities/plotting_utilities.py: confidence_ellipse
    # so the same would need to be done for qiRHi_covariances
    qiT_covariances = [ 19.994, -6.074, 16.576, -41.505 ]
    qiRHi_covariances = [ 1.777, 48.219, -1.8895, 259.9308 ]

    fig, ax = plt.subplots( nrows=2, ncols=2, figsize=(13,5.5) )
    lbl = [ r"$\bf{(a)}$ $\bf{C}$_1M1T1S", r'$\bf{(b)}$ $\bf{I}$_1M0T0S',
            r"$\bf{(c)}$ $\bf{C}$_2M1T1S", r'$\bf{(d)}$ $\bf{I}$_2M0T0S' ]
    farbe = [ cm.Oranges, cm.Oranges, cm.Blues, cm.Blues ]

    # If this input boolean is True, we add the in-situ IWC-T climatology line.
    if tiwc_line == True:
       T_MK, IWC_10_MK, _, IWC_50_MK, _, IWC_90_MK = martina_T_qi_perc_tropics()

    # Iterate through the five simulations
    for d, r, a, l, f, j in zip( datasets, raw, ax.reshape(-1), lbl, farbe, np.arange(4) ):
        if 'T' in histvals:
           h = a.imshow( d[histvals], origin='lower', cmap=f, extent=[190, 240, -3, 3.5],
               vmin=0, vmax=1, aspect=1.65 )
           # four quadrant lines and labels
           a.plot( [210, 237], [np.log10(10), np.log10(10)], linewidth=0.75, linestyle='--', color='red' )
           a.plot( [225, 225], [np.log10(10**(-3)), np.log10(10**3.5)], linewidth=0.75, ls='--', color='red' )
           a.text( 0.9, 0.9, 'I', c='red', fontsize=fs+2, transform=a.transAxes )
           a.text( 0.05, 0.73, 'II', c='red', fontsize=fs+2, transform=a.transAxes )
           a.text( 0.05, 0.05, 'III', c='red', fontsize=fs+2, transform=a.transAxes )
           a.text( 0.9, 0.05, 'IV', c='red', fontsize=fs+2, transform=a.transAxes )

        elif 'RHi' in histvals:
           h = a.imshow( d[histvals], origin='lower', cmap=f, extent=[60, 120, -3, 3.5],
                norm=colors.LogNorm(vmin=10**(-2),vmax=1), aspect=3.8 )
           # four quadrant lines and labels
           a.plot( [60, 120], [np.log10(10), np.log10(10)], linewidth=0.75, linestyle='--', color='red' )
           a.plot( [100, 100], [np.log10(10**(-3)), np.log10(10**3.5)], linewidth=0.75, ls='--', color='red' )
           a.text( 0.9, 0.9, 'I', c='red', fontsize=fs+2, transform=a.transAxes )
           a.text( 0.05, 0.73, 'II', c='red', fontsize=fs+2, transform=a.transAxes )
           a.text( 0.05, 0.05, 'III', c='red', fontsize=fs+2, transform=a.transAxes )
           a.text( 0.9, 0.05, 'IV', c='red', fontsize=fs+2, transform=a.transAxes )

        if tiwc_line == True:
           a.plot( T_MK, np.log10(IWC_10_MK), linewidth=1.25, linestyle='--', color='gray', alpha=alf )
           a.plot( T_MK, np.log10(IWC_50_MK), linewidth=2, linestyle='-', color='gray', alpha=alf )
           a.plot( T_MK, np.log10(IWC_90_MK), linewidth=1.25, linestyle='--', color='gray', alpha=alf )

        # If centroid == 0, no metric of central tendency added to the 2D pdf.
        # If centroid == 1, we add means to the 2D pdf.
        if centroid == 1:
           ym, _, ys, xm, _, xs = centroids( histvals, j )
           # First and third outputs are means. Second and fourth are medians.
           a.scatter( xm, np.log10(ym), marker='x', color='k', s=70, zorder=10 )
           if 'T' in histvals:
              cov = qiT_covariances[j]
           else:
              cov = qiRHi_covariances[j]
           _, _, e = stdev_bubble( xm, ym, xs, ys, cov, n_std=0.5 ) 
           a.add_patch( e )
           e.set_edgecolor( 'r' )
           e.set_linewidth( 1.5 )

        # If centroid == 2, we add medians to the 2D pdf.
        elif centroid == 2:
           _, ym, ys, _, xm, xs = centroids( histvals, j )
           a.scatter( xm, np.log10(ym), marker='x', color='k', s=70, zorder=10 )

        if j == 1 or j == 3:
           cb = fig.colorbar( h, ax=ax[int(j/2),:], shrink=0.75 )
           cb.ax.tick_params(labelsize=fs+3)
           cb.ax.set_ylabel('Probability [%]', fontsize=fs+2)

        a.set_xlim( [xmin, xmax] )
        a.set_ylim( [-3, 3.5] )
        if j == 0 or j == 2:
           a.set_yticks( [ymin, ymin+2, ymin+4, ymin+6] )
           a.set_yticklabels( [r'10$^{-3}$', r'10$^{-1}$', r'10$^{:1d}$'.format(ymin+4),
                   r'10$^{:1d}$'.format(ymin+6)] )
        else:
           a.set_yticks( [ymin+2, ymin+4, ymin+6] )
           a.set_yticklabels( [r'10$^{-1}$', r'10$^{:1d}$'.format(ymin+4),
                   r'10$^{:1d}$'.format(ymin+6)] )
        a.text( 0.02, 1.05, l, fontsize=fs, transform=a.transAxes )
        sexy_axes( a, fs+2 )

    if xvar == 'T':
       xl = "Temperature [K]"
    if xvar == 'RHi':
       xl = r"RH$_i$ [%]"
    if yvar == 'qi':
       yl = r"$q_i$ [ppmv]"
    if yvar == 'Ni':
       yl = r"$N_i$ [L$^{-1}$]"

    ax[0,0].set_ylabel( yl, fontsize=fs+3 )
    ax[1,0].set_ylabel( yl, fontsize=fs+3 )
    ax[1,1].set_xlabel( xl, fontsize=fs+3 )
#    ax[2,0].set_ylabel( yl, fontsize=fs+3 )
#    ax[2,0].set_xlabel( xl, fontsize=fs+3 )
    ax[1,0].set_xlabel( xl, fontsize=fs+3 )
#    ax[2,1].set_visible('')

#    cb = fig.colorbar(h, ax=ax[2,1])
#    cb.ax.tick_params(labelsize=fs+3)
#    cb.ax.set_ylabel('Probability [%]', fontsize=fs+3)
#    plt.tight_layout()

    if figsave == True:
       print('figsave')
       suffix = ''
       if centroid == True:
          cstr = '_centroid'
       else:
          cstr = ''
       #bd = '/work/bb1018/b380873/tropic_vis/output/'
       bd = '/xdisk/sylvia/tropic_vis/output/'
       fig.savefig( bd + 'CLaMS-ICON-' + yvar + '-' + xvar + '-density-norm' + cstr + suffix + '.pdf' )


# Return the mean or median variables for a variable (or two) denoted by histvals
# and a simulation denoted by sim_tag. sim_tag = [0, 5) with the usual ordering:
# 0 = CLaMS-Tf-0V1M0A0R, 1 = ICON-0V1M0A0R, 2 = CLaMS-Tf-0V2M0A0R, 3 = ICON-0V2M0A0R,
# 4 = CLaMS-0V2M0A0R
def centroids( histvals, sim_tag ):
    import numpy as np

    # One-dimensional
    # These values were calculated from all qi > 10^(-8) g kg-1
    #qi_mean = [ 30.1573, 12.815, 50.063, 17.56, 49.5122, 53.43395 ]
    #qi_med = [ 3.999, 2.513, 10.706, 0.0731, 9.4459, 16.6216 ]

    # These values are calculated only within the bin range in Fig 3
    qi_mean = [ 29.966, 17.825, 56.830, 33.809, 68.958, 67.154 ]
    qi_med = [ 11.308, 11.086, 22.287, 10.035, 26.635, 28.468 ]
    qi_std = [ 70.154, 27.13, 132.66, 71.84, 154.49, 162.75 ]

    T_mean = [ 229.6377, 228.16, 225.469, 220.01, 225.433, 224.494 ]
    T_med = [ 229.808, 230.37, 225.975, 227.54, 225.906, 225.192 ]
    T_std = [ 5.13, 11.21, 6.98, 15.63, 7.0, 7.07 ]

    # These values were calculated from all qi > 10^(-8) g kg-1
    #qi_outflow_mean = [ 25.339, 13.007, 47.548, 24.020, 46.835, 52.0328 ]
    #qi_outflow_med = [ 3.467, 3.349, 10.345, 1.400, 9.0512, 16.7797 ]

    # These values are calculated only within the bin range in Fig 3
    qi_outflow_mean = [ 27.284, 17.3988, 54.297, 32.366, 65.387, 65.477 ]
    qi_outflow_med = [ 10.637, 10.974, 21.759, 9.799, 25.502, 28.628 ]
    qi_outflow_std = [ 63.348, 26.980, 125.47, 84.43, 145.95, 157.26 ]

    T_outflow_mean = [ 228.793, 229.767, 225.244, 229.05, 225.204, 224.513 ]
    T_outflow_med = [ 229.2277, 230.4299, 225.77, 230.159, 225.699, 225.16 ]
    T_outflow_std = [ 4.60, 4.17, 6.14, 5.41, 6.15, 6.27 ]

    # These values were calculated from all qi > 10^(-8) g kg-1
    #qi_insitu_mean = [ 163.78, 0.0384, 46.214, 0.4429, 44.947, 36.62998 ]
    #qi_insitu_med = [ 56.115, 0.00135, 7.389, 0.0004155, 5.233, 9.1968 ]

    # These values are calculated only within the bin range in Fig 3
    qi_insitu_mean = [ 50.99, 12.967, 68.6266, 48.608, 70.01, 43.801 ]
    qi_insitu_med = [ 37.188, 6.25, 24.265, 12.344, 29.146, 12.386 ]
    qi_insitu_std = [ 98.84, 0.404, 171.47, 16.18, 165.61, 167.92 ] 

    T_insitu_mean = [ 206.966, 194.991, 207.71, 198.039, 207.8228, 207.892 ]
    T_insitu_med = [ 207.95, 195.19, 208.349, 198.1322, 208.428, 208.4407 ]
    T_insitu_std = [ 0.987, 1.24, 2.43, 2.495, 2.259, 2.122 ]

    qi_flight_mean = [ 21.8905, 12.62, 10.213, 4.248, 9.4398, 14.7689 ]
    qi_flight_med = [ 2.6432, 3.799, 1.476, 0.0544, 1.1227, 5.8066 ]
    qi_flight_std = [ 57.42, 26.66, 30.356, 16.74, 34.263, 33.947 ]

    T_flight_mean = [ 225.061, 226.3257, 220.506, 217.581, 220.4409, 219.554 ]
    T_flight_med = [ 225.061, 226.4384, 220.640, 223.613, 220.603, 219.429 ]
    T_flight_std = [ 4.60, 4.55, 5.84, 14.45, 5.81, 6.09 ]

    # The second element of the Ni lists should always be an np.nan as ICNC are not output from ICON-0V1M0A0R
    # These values were calculated from all Ni > 10^(-8) L-1
    #Ni_mean = [ 555.956, np.nan, 692.665, 1132.75, 685.620, 536.199 ]
    #Ni_med = [ 2.869, np.nan, 17.6179, 0.7372, 13.2077, 24.2849 ]

    # These values are calculated only within the bin range in Fig 3
    Ni_mean = [ 871.364, np.nan, 1068.07, 1370.56, 985.43, 683.65 ]
    Ni_med = [ 22.478, np.nan, 64.041, 10.156, 60.737, 57.090 ]
    Ni_std = [ 6333.5, np.nan, 4517.9, 5748.9, 4476.8, 2762.4 ]

    RHi_mean = [ 96.566, 91.621, 98.556, 74.803, 98.831, 102.335 ]
    RHi_med = [ 97.998, 96.7814, 99.335, 85.245, 99.505, 100.421 ]
    RHi_std = [ 14.97, 14.94, 13.90, 29.45, 19.87, 12.43 ]

    # These values were calculated from all Ni > 10^(-8) L-1
    #Ni_outflow_mean = [ 585.261, np.nan, 664.354, 1632.38, 658.524, 522.13871 ]
    #Ni_outflow_med = [ 2.478, np.nan, 17.2353, 4.839, 12.761, 23.9566 ]

    # These values are calculated only within the bin range in Fig 3
    Ni_outflow_mean = [ 941.58, np.nan, 1019.94, 1476.31, 950.0, 666.59 ]
    Ni_outflow_med = [ 23.15, np.nan, 63.956, 11.162, 59.891, 56.523 ]
    Ni_outflow_std = [ 6563.6, np.nan, 4374.7, 7178.9, 4377.4, 2568.4 ]

    RHi_outflow_mean = [ 97.552, np.nan, 99.273, 89.304, 99.573, 0 ]
    RHi_outflow_med = [ 97.843, np.nan, 99.314, 92.848, 99.474,0 ]
    RHi_outflow_std = [ 15.33, 9.66, 13.91, 14.62, 18.11, 12.39 ]

    # These values were calculated from all Ni > 10^(-8) L-1
    #Ni_insitu_mean = [ 44797.53, np.nan, 3379.066, 55.224, 3251.917, 1575.3982 ]
    #Ni_insitu_med = [ 20825.68, np.nan, 154.44, 0.01459, 72.17, 61.09877 ]

    # These values are calculated only within the bin range in Fig 3
    Ni_insitu_mean = [ 46340.43, np.nan, 4281.91, 498.16, 4292.477, 1799.07 ]
    Ni_insitu_med = [ 2.929*10**4, np.nan, 520.436, 2.776, 438.82, 97.4098 ]
    Ni_insitu_std = [ 28573.82, np.nan, 10142.6, 1993, 9835.9, 7302.73 ]

    RHi_insitu_mean = [ 67.069, np.nan, 95.849, 32.7418, 95.179, 0 ]
    RHi_insitu_med = [ 74.091, np.nan, 98.545, 28.254, 98.493, 0 ]
    RHi_insitu_std = [ 11.46, 10.02, 18.19, 16.64, 62.76, 15.92 ]

    Ni_flight_mean = [ 1834.39, np.nan, 337.60, 61.868, 366.348, 242.3075 ]
    Ni_flight_med = [ 5.993, np.nan, 2.510, 0.4592, 1.5065, 11.0267 ]
    Ni_flight_std = [ 9939.1, np.nan, 2274.7, 437.997, 4828.86, 941.71 ]

    RHi_flight_mean = [ 96.699, np.nan, 101.545, 74.808, 102.00, 0 ]
    RHi_flight_med = [ 97.727, np.nan, 99.9767, 85.416, 100.125, 0 ]
    RHi_flight_std = [ 16.68, 9.59, 13.65, 27.01, 13.95, 12.40 ]

    # Two-dimensional
    qiT_mean = [ [28.37, 14.68, 63.64, 18.02, np.nan, np.nan], [229.15, 227.76, 225.08, 218.23, np.nan, np.nan] ]
    qiT_med = [ [2.18, 1.27, 7.50, 0.064, np.nan, np.nan], [229.13, 230.3, 225.63, 227.63, np.nan, np.nan] ]
    qiT_std = [ [70.15, 27.13, 132.65, 71.83, 154.5, 162.76], [5.13, 11.21, 6.98, 15.63, 7.0, 7.068] ]

    qiT_outflow_mean = [ [25.56, 28.89, 60.68, 26.54, np.nan, np.nan], [228.43, 229.74, 224.95, 228.83, np.nan, np.nan] ]
    qiT_outflow_med = [ [2.033, 2.16, 7.32, 1.18, np.nan, np.nan], [228.6, 230.2, 225.5, 230.04, np.nan, np.nan] ]
    qiT_outflow_std = [ [63.35, 26.98, 125.47, 84.43, 145.95, 157.27], [4.6, 4.17, 6.14, 5.41, 6.15, 6.27] ]

    qiT_insitu_mean = [ [46.4, 0.0105, 46.09, 0.436, np.nan, np.nan], [208.98, 194.98, 207.71, 198.04, np.nan, np.nan] ]
    qiT_insitu_med = [ [33.5, 0.00134, 6.43, 0.000416, np.nan, np.nan], [209.3, 195.19, 208.36, 198.13, np.nan, np.nan] ]
    qiT_insitu_std = [ [98.84, 0.404, 171.47, 16.18, 165.6, 167.92], [0.967, 1.247, 2.430, 2.49, 2.259, 2.12] ]

    qiT_flight_mean = [ [18.48, 10.0, 9.40, 3.244, np.nan, np.nan], [225.5, 226.98, 220.4677, 217.29, np.nan, np.nan] ]
    qiT_flight_med = [ [1.81, 2.078, 1.409, 0.0324, np.nan, np.nan], [225.4, 226.9, 220.6, 223.12, np.nan, np.nan] ]
    qiT_flight_std = [ [57.42, 26.66, 30.35, 16.74, 34.26, 33.95], [4.6, 4.55, 5.83, 14.45, 5.81, 6.09] ]

    qiRHi_mean = [ [17.64, 10.03, 39.57, 21.36, np.nan, np.nan], [98.66, 88.89, 100.07, 81.17, np.nan, np.nan] ]
    qiRHi_med = [ [2.18, 1.27, 7.50, 0.064, np.nan, np.nan], [98.12, 95.24, 99.43, 81.8, np.nan, np.nan] ]

    qiRHi_outflow_mean = [ [25.89, 18.16, 60.68, 30.55, np.nan, np.nan], [98.75, 96.55, 100.15, 97.05, np.nan, np.nan] ] #15.89, 10.16, 37.72, 22.3? 88.05?
    qiRHi_outflow_med = [ [2.033, 2.16, 7.32, 1.18, np.nan, np.nan], [98.08, 96.44, 99.40, 91.94, np.nan, np.nan] ]
    qiRHi_outflow_std = [ [63.35, 26.98, 125.47, 84.43, np.nan, np.nan], [15.33, 9.48, 13.91, 13.98, np.nan, np.nan] ]

    qiRHi_insitu_mean = [ [46.4, 0.0105, 46.09, 0.436, np.nan, np.nan], [95.27, 53.24, 97.55, 33.63, np.nan, np.nan] ]
    qiRHi_insitu_med = [ [33.5, 0.00134, 6.43, 0.000416, np.nan, np.nan], [95.21, 51.4, 98.77, 29.34, np.nan, np.nan] ]

    qiRHi_flight_mean = [ [18.48, 10.0, 9.40, 3.244, np.nan, np.nan], [98.19, 92.39, 101.58, 73.55, np.nan, np.nan] ]
    qiRHi_flight_med = [ [1.81, 2.078, 1.409, 0.0324, np.nan, np.nan], [98.13, 96.22, 99.96, 83.5, np.nan, np.nan] ]

    s = sim_tag
    whichfields = {'qi': [qi_mean[s], qi_med[s], qi_std[s]],
       'qi_outflow': [qi_outflow_mean[s], qi_outflow_med[s], qi_outflow_std[s]],
       'qi_insitu': [qi_insitu_mean[s], qi_insitu_med[s], qi_insitu_std[s]],
       'qi_flight': [qi_flight_mean[s], qi_flight_med[s], qi_flight_std[s]],
       'T': [T_mean[s], T_med[s], T_std[s]], 
       'T_outflow': [T_outflow_mean[s], T_outflow_med[s], T_outflow_std[s]],
       'T_insitu': [T_insitu_mean[s], T_insitu_med[s], T_insitu_std[s]],
       'T_flight': [T_flight_mean[s], T_flight_med[s], T_flight_std[s]],
       'Ni': [Ni_mean[s], Ni_med[s], Ni_std[s]],
       'Ni_outflow': [Ni_outflow_mean[s], Ni_outflow_med[s], Ni_outflow_std[s]],
       'Ni_insitu': [Ni_insitu_mean[s], Ni_insitu_med[s], Ni_insitu_std[s]],
       'Ni_flight': [Ni_flight_mean[s], Ni_flight_med[s], Ni_flight_std[s]],
       'RHi': [RHi_mean[s], RHi_med[s], RHi_std[s]],
       'RHi_outflow': [RHi_outflow_mean[s], RHi_outflow_med[s], RHi_outflow_std[s]],
       'RHi_insitu': [RHi_insitu_mean[s], RHi_insitu_med[s], RHi_outflow_std[s]],
       'RHi_flight': [RHi_flight_mean[s], RHi_flight_med[s], RHi_outflow_std[s]],
       'qiTh': [qiT_mean[0][s], qiT_med[0][s], qiT_std[0][s],
                qiT_mean[1][s], qiT_med[1][s], qiT_std[1][s]],
       'qiTh_outflow': [qiT_outflow_mean[0][s], qiT_outflow_med[0][s], qiT_outflow_std[0][s],\
                        qiT_outflow_mean[1][s], qiT_outflow_med[1][s], qiT_outflow_std[1][s]],
       'qiTh_insitu': [qiT_insitu_mean[0][s], qiT_insitu_med[0][s], qiT_insitu_std[0][s],\
                       qiT_insitu_mean[1][s], qiT_insitu_med[1][s], qiT_insitu_std[1][s]],
       'qiTh_flight': [qiT_flight_mean[0][s], qiT_flight_med[0][s], qiT_flight_std[0][s],\
                       qiT_flight_mean[1][s], qiT_flight_med[1][s], qiT_flight_std[1][s]],
       'qiRHih': [qiRHi_mean[0][s], qiRHi_med[0][s], qiRHi_mean[1][s], qiRHi_med[1][s], ],
       'qiRHih_outflow': [qiRHi_outflow_mean[0][s], qiRHi_outflow_med[0][s], qiRHi_outflow_std[0][s],\
                          qiRHi_outflow_mean[1][s], qiRHi_outflow_med[1][s], qiRHi_outflow_std[1][s]],
       'qiRHih_insitu': [qiRHi_insitu_mean[0][s], qiRHi_insitu_med[0][s], qiRHi_insitu_mean[1][s], qiRHi_insitu_med[1][s]],
       'qiRHih_flight': [qiRHi_flight_mean[0][s], qiRHi_flight_med[0][s], qiRHi_flight_mean[1][s], qiRHi_flight_med[1][s]],
       'NiTh': [Ni_mean[s], Ni_med[s], T_mean[s], T_med[s]],
       'NiTh_outflow': [Ni_outflow_mean[s], Ni_outflow_med[s], T_outflow_mean[s], T_outflow_med[s]],
       'NiTh_insitu': [Ni_insitu_mean[s], Ni_insitu_med[s], T_insitu_mean[s], T_insitu_med[s]],
       'NiTh_flight': [Ni_flight_mean[s], Ni_flight_med[s], T_flight_mean[s], T_flight_med[s]],
       'NiRHih': [Ni_mean[s], Ni_med[s], RHi_mean[s], RHi_med[s]],
       'NiRHih_outflow': [Ni_outflow_mean[s], Ni_outflow_med[s], RHi_outflow_mean[s], RHi_outflow_med[s]],
       'NiRHih_insitu': [Ni_insitu_mean[s], Ni_insitu_med[s], RHi_insitu_mean[s], RHi_insitu_med[s]],
       'NiRHih_flight': [Ni_flight_mean[s], Ni_flight_med[s], RHi_flight_mean[s], RHi_flight_med[s]] }

    return whichfields[histvals]

