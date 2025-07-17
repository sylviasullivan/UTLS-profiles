# Input the initial and final times to read as time0 and timef.
# Time range from Lee et al. 2019 (6:20-6:48 UTC)
def read_flighttrack( time0, timef ):
    import xarray as xr

    # Read in-situ data
    # In-situ not filtered for whole-second values
    #daten = xr.open_dataset('obs/stratoclim2017.geophysika.0808_1.master.ci_eval.nc')
    bd = '/groups/sylvia/UTLS-profiles/'
    daten = xr.open_dataset( bd + 'obs/stratoclim2017.geophysika.0808_1.filtered_per_sec.nc' )

    # Extract values between time0 and timef
    zeit = daten['time'].sel( time=slice(time0, timef) )
    alt = daten['BEST:ALT'].sel( time=slice(time0, timef) )
    qv_flash = daten['BEST:H2O_gas'].sel( time=slice(time0, timef) )
    qv_fish = daten['BEST:H2O_enh'].sel( time=slice(time0, timef) )
    qi = daten['BEST:IWC'].sel( time=slice(time0, timef) )
    temp = daten['BEST:TEMP'].sel( time=slice(time0, timef) )
    pressure = daten['BEST:PRESS'].sel( time=slice(time0, timef) )
    theta = daten['BEST:THETA'].sel( time=slice(time0, timef) )
    rhice_flash = daten['BEST:RH_ice_gas'].sel( time=slice(time0, timef) )
    rhice_fish = daten['BEST:RH_ice_enh'].sel( time=slice(time0, timef) )

    #lat = daten['BEST:LAT'].sel( time=slice(time0, timef) )
    #lon = daten['BEST:LON'].sel( time=slice(time0, timef) )
    #print('In-situ lat min: ' + str(lat.min(skipna=True).values) + ' // In-situ lat max: ' + str(lat.max(skipna=True).values))
    #print('In-situ lon min: ' + str(lon.min(skipna=True).values) + ' // In-situ lon max: ' + str(lon.max(skipna=True).values))

    # Extract corresponding altitudes and times for different variables according to their non-zero values
    alt1 = alt.where( (alt > 0) & (qv_flash > 0) & (qv_fish > 0) ).values
    t1 = zeit.where( (alt > 0) & (qv_flash > 0) & (qv_fish > 0) )
    qv_flash = qv_flash.where( (alt > 0) & (qv_flash > 0) & (qv_fish > 0) )
    qv_fish = qv_fish.where( (alt > 0) & (qv_flash > 0) & (qv_fish > 0) )

    alt2 = alt.where( (alt > 0) & (qi > 0) )
    qi = qi.where( (alt > 0) & (qi > 0) )

    alt3 = alt.where( (temp > 0) & (theta > 0) )
    temp = temp.where( (temp > 0) & (theta > 0) )
    theta = theta.where( (temp > 0) & (theta > 0) )

    alt4 = alt.where( (rhice_flash > 0) & (rhice_fish > 0) )
    rhice_flash = rhice_flash.where( (rhice_flash > 0) & (rhice_fish > 0) )
    rhice_fish = rhice_fish.where( (rhice_flash > 0) & (rhice_fish > 0) )

    return alt1, qv_flash, qv_fish, alt2, qi, alt3, temp, theta, alt4, rhice_flash, rhice_fish


# Group the flight track values into altitudinal bins from min_alt to max_alt
def bin_flighttrack( min_alt, max_alt, alt1, qv_flash, qv_fish, alt2, qi, alt3, temp, theta, alt4, rhice_flash, rhice_fish ):
    import xarray as xr
    import numpy as np

    basedir = '/groups/sylvia/UTLS-profiles/'

    # Define the simulation bins from the vertical grid file
    vgrid = xr.open_dataset(basedir + 'vgrid_icon-grid_tropic_55e115e5s40n.nc')
    alt = vgrid.vct_a.values[:,0]
    j = np.argwhere( (alt >= min_alt) & (alt <= max_alt) )
    bins_sims = alt[j[:,0]]

    # Binning in altitude between <u> and <d> with <n> bins, which elements go in which bin?
    # Make a multidimensional list of alt and h2o values in each.
    #u = 14000
    #d = 22000
    #n = 70

    # np.digitize returns the indices of the bins to which each element in alt* belongs.
    #i1 = np.digitize( alt1, bins=np.linspace(u,d,n) )
    #i2 = np.digitize( alt2, bins=np.linspace(u,d,n) )
    #i3 = np.digitize( alt3, bins=np.linspace(u,d,n) )

    # np.digitize returns the indices of the bins to which each element in alt* belongs.
    icon_n = len(bins_sims)
    i1 = np.digitize( alt1, bins=bins_sims )
    i2 = np.digitize( alt2, bins=bins_sims )
    i3 = np.digitize( alt3, bins=bins_sims )
    i4 = np.digitize( alt4, bins=bins_sims )

    alt1_list = [ [] for i in np.arange(icon_n) ]
    qv_flash_list = [ [] for i in np.arange(icon_n) ]
    qv_fish_list = [ [] for i in np.arange(icon_n) ]

    alt2_list = [ [] for i in np.arange(icon_n) ]
    qi_list = [ [] for i in np.arange(icon_n) ]

    alt3_list = [ [] for i in np.arange(icon_n) ]
    temp_list = [ [] for i in np.arange(icon_n) ]
    theta_list = [ [] for i in np.arange(icon_n) ]

    alt4_list = [ [] for i in np.arange(icon_n) ]
    RHi_list = [ [] for i in np.arange(icon_n) ]

    # Group values into these bins
    for elem_idx, group_idx in enumerate(i1):
        alt1_list[group_idx-1].append( alt1[elem_idx].item() )
        qv_flash_list[group_idx-1].append( qv_flash[elem_idx].item() )
        qv_fish_list[group_idx-1].append( qv_fish[elem_idx].item() )

    for elem_idx, group_idx in enumerate(i2):
        alt2_list[group_idx-1].append( alt2[elem_idx].item() )
        qi_list[group_idx-1].append( qi[elem_idx].item() )

    for elem_idx, group_idx in enumerate(i3):
        alt3_list[group_idx-1].append( alt3[elem_idx].item() )
        temp_list[group_idx-1].append( temp[elem_idx].item() )
        theta_list[group_idx-1].append( theta[elem_idx].item() )

    for elem_idx, group_idx in enumerate(i4):
        alt4_list[group_idx-1].append( alt4[elem_idx].item() )
        RHi_list[group_idx-1].append( rhice_flash[elem_idx].item() )

    # Calculate the statistics across all items in a bin if there are at least 5 such items
    temp_SC_stats = np.empty((3, icon_n))
    temp_SC_stats[:] = np.nan
    theta_SC_stats = np.empty((3, icon_n))
    theta_SC_stats[:] = np.nan
    qv_flash_SC_stats = np.empty((3, icon_n))
    qv_flash_SC_stats[:] = np.nan
    qv_fish_SC_stats = np.empty((3, icon_n))
    qv_fish_SC_stats[:] = np.nan
    qi_SC_stats = np.empty((3, icon_n))
    qi_SC_stats[:] = np.nan
    RHi_SC_stats = np.empty((3, icon_n))
    RHi_SC_stats[:] = np.nan

    ## This chunk of code is generally commented out as we only need to save
    ## the number of elements in a bin from the in-situ measurements once
    ## These number of elements are used in syn_traj_stats_fixed
    #temp_len = []
    #qv_flash_len = []
    #qi_len = []
    #theta_len = []
    #rhi_len = []
    #for i in np.arange(icon_n):
    #    temp_len.append( int(len(temp_list[i])) )
    #    qv_flash_len.append( int(len(qv_flash_list[i])) )
    #    qi_len.append( int(len(qi_list[i])) )
    #    theta_len.append( int(len(theta_list[i])) )
    #    rhi_len.append( int(len(RHi_list[i])) )
    #
    ## The whole second set of trajectories (z ~ 22 km) are piled into the last bin.
    ## Remove this bin as we're interested in the vertical profile lower down.
    #temp_len[-1] = 0
    #qv_flash_len[-1] = 0
    #qi_len[-1] = 0
    #theta_len[-1] = 0
    #rhi_len[-1] = 0
    #np.save( basedir + 'output/Stratoclim_temp_len.npy', np.asarray(temp_len, dtype='i4') )
    #np.save( basedir + 'output/Stratoclim_qv_len.npy', np.asarray(qv_len, dtype='i4') )
    #np.save( basedir + 'output/Stratoclim_qi_len.npy', np.asarray(qi_len, dtype='i4') )
    #np.save( basedir + 'output/Stratoclim_theta_len.npy', np.asarray(theta_len, dtype='i4') )
    #np.save( basedir + 'output/Stratoclim_rhi_len.npy', np.asarray(rhi_len, dtype='i4') )
    ##

    for i in np.arange(icon_n):
        if (len(temp_list[i]) > 5):
            temp_SC_stats[0,i] = np.nanmean( temp_list[i] )
            temp_SC_stats[1,i] = np.nanmedian( temp_list[i] )
            temp_SC_stats[2,i] = np.nanstd( temp_list[i] )
            theta_SC_stats[0,i] = np.nanmean( theta_list[i] )
            theta_SC_stats[1,i] = np.nanmedian( theta_list[i] )
            theta_SC_stats[2,i] = np.nanstd( theta_list[i] )
        if (len(qv_flash_list[i]) > 5):
            qv_flash_SC_stats[0,i] = np.nanmean( qv_flash_list[i] )
            qv_flash_SC_stats[1,i] = np.nanmedian( qv_flash_list[i] )
            qv_flash_SC_stats[2,i] = np.nanstd( qv_flash_list[i] )
        if (len(qv_fish_list[i]) > 5):
            qv_fish_SC_stats[0,i] = np.nanmean( qv_fish_list[i] )
            qv_fish_SC_stats[1,i] = np.nanmedian( qv_fish_list[i] )
            qv_fish_SC_stats[2,i] = np.nanstd( qv_fish_list[i] )
        if (len(qi_list[i]) > 5):
            qi_SC_stats[0,i] = np.nanmean( qi_list[i] )
            qi_SC_stats[1,i] = np.nanmedian( qi_list[i] )
            qi_SC_stats[2,i] = np.nanstd( qi_list[i] )
        if (len(RHi_list[i]) > 5):
            RHi_SC_stats[0,i] = np.nanmean( RHi_list[i] )
            RHi_SC_stats[1,i] = np.nanmedian( RHi_list[i] )
            RHi_SC_stats[2,i] = np.nanstd( RHi_list[i] )

    return bins_sims, temp_SC_stats, theta_SC_stats, qv_flash_SC_stats, qv_fish_SC_stats, qi_SC_stats, RHi_SC_stats


# Utility function to retain only the whole-second measurements in the StratoClim data.
def trimDataTime():
    from netCDF4 import num2date, Dataset
    import xarray as xr
    import matplotlib.pyplot as plt
    import sys, time

    basedir = '/groups/sylvia/UTLS-profiles/obs/'
    fi = basedir + 'stratoclim2017.geophysika.0808_1.master.ci_eval.nc'
    Stratoclim = Dataset(fi, 'r+')

    daten = num2date(times=Stratoclim.variables['time'][:],units='seconds since 2000-01-01 00:00:00 UTC')
    # indices to retain associated with whole-second measurements
    indx = [i for i, d in enumerate(daten) if d.microsecond == 0]

    # recast Stratoclim as an xarray dataset now; Stratoclim2 will hold only whole-second measurements
    Stratoclim = xr.open_dataset(fi)
    Stratoclim2 = xr.Dataset()

    # iterate over the variables in the StratoClim file
    for v in Stratoclim.variables:
        Stratoclim2[v] = Stratoclim[v].isel(time=indx)
    Stratoclim2.to_netcdf(basedir + 'stratoclim2017.geophysika.0808_1.filtered_per_sec.nc')

