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

    # Extract corresponding pressures and times for different variables according to their non-zero values
    p1 = pressure.where( (qv_flash > 0) & (qv_fish > 0) ).values
    qv_flash = qv_flash.where( (qv_flash > 0) & (qv_fish > 0) )
    qv_fish = qv_fish.where( (qv_flash > 0) & (qv_fish > 0) )

    p2 = pressure.where( qi > 0 )
    qi = qi.where( qi > 0 )

    p3 = pressure.where( (temp > 0) & (theta > 0) )
    temp = temp.where( (temp > 0) & (theta > 0) )
    theta = theta.where( (temp > 0) & (theta > 0) )

    p4 = pressure.where( (rhice_flash > 0) & (rhice_fish > 0) )
    rhice_flash = rhice_flash.where( (rhice_flash > 0) & (rhice_fish > 0) )
    rhice_fish = rhice_fish.where( (rhice_flash > 0) & (rhice_fish > 0) )

    return p1, qv_flash, qv_fish, p2, qi, p3, temp, theta, p4, rhice_flash, rhice_fish


# Group the flight track values into pressure bins
def bin_flighttrack_general( plevs, p1, qv_flash, qv_fish, p2, qi, p3, temp, theta, p4, rhice_flash, rhice_fish ):
    import xarray as xr
    import numpy as np

    def closest_plev_idx( pvals, plevs ):
        pvals = np.asarray( pvals )
        return np.argmin( np.abs(pvals[:, np.newaxis] - plevs[np.newaxis, :]), axis=1 )
        
    # For the four sets of pressure values, get closest indices in plevs
    #print( p1.shape, plevs.shape )
    i1 = closest_plev_idx( p1*100, plevs )  # convert observed pressures hPa -> Pa
    i2 = closest_plev_idx( p2*100, plevs )
    i3 = closest_plev_idx( p3*100, plevs )
    i4 = closest_plev_idx( p4*100, plevs )
    nlevs = len(plevs)

    def init_bin_list(): return [[] for _ in range(nlevs)]

    qv_flash_list = init_bin_list()
    qv_fish_list = init_bin_list()
    qi_list = init_bin_list()
    temp_list = init_bin_list()
    theta_list = init_bin_list()
    RHi_list = init_bin_list()

    # Group values for bins
    for idx, bin_idx in enumerate(i1):
        qv_flash_list[bin_idx].append( qv_flash[idx] )
        qv_fish_list[bin_idx].append( qv_fish[idx] )
    for idx, bin_idx in enumerate(i2):
        qi_list[bin_idx].append(qi[idx])
    for idx, bin_idx in enumerate(i3):
        temp_list[bin_idx].append(temp[idx])
        theta_list[bin_idx].append(theta[idx])
    for idx, bin_idx in enumerate(i4):
        RHi_list[bin_idx].append(rhice_flash[idx])

    def compute_stats(binned_list):
        stats = np.full((3, nlevs), np.nan)
        for i, values in enumerate(binned_list):
            if len(values) > 5:
                values = np.array(values)
                stats[0, i] = np.nanmean(values)
                stats[1, i] = np.nanmedian(values)
                stats[2, i] = np.nanstd(values)
        return stats

    return ( plevs, compute_stats(temp_list), compute_stats(theta_list),
             compute_stats(qv_flash_list), compute_stats(qv_fish_list),
             compute_stats(qi_list), compute_stats(RHi_list) )


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

