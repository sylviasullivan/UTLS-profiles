# Input the existing syn_traj Dataset along with time, pressure, lat, and lon from the flight track
#@profile
def pinpointSim(syn_traj, var_ICON, flight_time, Stratoclim_vals, sim_acronym):
    import datetime, sys, time
    import pandas as pd
    import numpy as np
    import xarray as xr
    from timeround10 import timeround10
    from var_dict import var_dict
    var_dict = var_dict()

    # Global variables in the script form
    n = 5
    ll_interval = 0.75
    alt_interval = 1
    mw_dryair = 28.97*1000    # kg air (mol air)-1
    mw_watvap = 18.02*1000    # kg wv (mol wv)-1
    conv = mw_dryair / mw_watvap

    # Find the nearest whole 10-min time.
    flight_time_approx = timeround10(flight_time)

    # Construct the time window to extract.
    early_time = flight_time_approx - datetime.timedelta(minutes=30)
    late_time = flight_time_approx + datetime.timedelta(minutes=30)

    # Find indices corresponding to ICON pressure levels above + below the closest flight track match.
    basedir = '/work/bb1018/b380873/tropic_vis/remapping/'
    sim_pressures = np.loadtxt(basedir + 'PMEAN_48-72.txt')
    flight_pressure = Stratoclim_vals['BEST:PRESS'].values*100  # [Pa]
    i = np.argmin(np.abs(flight_pressure - sim_pressures))
    if i < 1 or i > 117:
        raise Exception('Flight pressure outside of simulation range.')
    var_ICON = var_ICON.isel( plev=slice(i-alt_interval, i+alt_interval+1) )

    # Extract the time and lat-lon intervals
    flight_lat = Stratoclim_vals['BEST:LAT'].values
    flight_lon = Stratoclim_vals['BEST:LON'].values
    var_ICON = var_ICON.sel( time=slice(early_time, late_time),
                             lat=slice(flight_lat-ll_interval, flight_lat+ll_interval),
                             lon=slice(flight_lon-ll_interval, flight_lon+ll_interval) )

    mini_traj = xr.Dataset( data_vars=dict(
                            temp=( ["time", "ntraj"], np.empty([1,1]) ),
                            air_pressure=( ["time", "ntraj"], np.empty([1,1]) ),
                            qv=( ["time", "ntraj"], np.empty([1,1]) ),
                            qi=( ["time", "ntraj"], np.empty([1,1]) ),
                            lat=( ["time", "ntraj"], np.empty([1,1]) ),
                            lon=( ["time", "ntraj"], np.empty([1,1]) ),
                            alt=( ["time", "ntraj"], np.empty([1,1]) ),
                           ),
                       coords=dict( time=[flight_time], ntraj=[1] ) )

    for v in var_dict.keys():
        v1 = var_dict[v]
        mini_traj[v1] = np.nan # So that we do not get crazy values from np.empty
        sc_val = Stratoclim_vals[v].values
        # If you are looking at pressure, convert to Pa
        if v == 'BEST:PRESS':
            sc_val = sc_val*100
        # If you are looking at ice or vapor mixing ratio, convert to kg kg-1 from ppmv
        if v == 'BEST:H2O_gas' or v == 'BEST:IWC':
            sc_val = sc_val / conv / 10**6

        # Only choose a closest numerical value if the in-situ one is not a nan.
        if np.isnan(sc_val) == False:
           icon_vals = var_ICON[v1].values.flatten()
           j = np.argmin(np.abs(sc_val-icon_vals))
           mini_traj[v1] = ( ["time", "ntraj"], icon_vals[j]*np.ones((1,1)) )
        else:
          mini_traj[v1] = ( ["time", "ntraj"], np.nan*np.ones((1,1)) )

    mini_traj['alt'] = ( ["time", "ntraj"], Stratoclim_vals['BEST:ALT'].values*np.ones((1,1)) )
    syn_traj = xr.concat( [syn_traj, mini_traj], dim='time' )

    return syn_traj

#profilewrapper()
