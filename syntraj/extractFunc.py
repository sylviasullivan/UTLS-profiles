# Input the existing syn_traj Dataset along with time, pressure, lat, and lon from the flight track
def extractFunc( syn_traj, var_ICON, flight_time, flight_pressure, flight_lat, flight_lon, flight_alt, n_traj, ll_int ):
    import datetime, sys
    import numpy as np
    import xarray as xr
    import sys, time
    from timeround10 import timeround10
    ri = np.random.randint

    # Find the nearest whole 10-min time.
    flight_time_approx = timeround10(flight_time)

    # Check if flight_time_approx is within the ICON time range
    time_min = var_ICON.time.min().values
    time_max = var_ICON.time.max().values

    traj_vars = {}
    m = 1
    if not (time_min <= np.datetime64(flight_time_approx) <= time_max):
        # Fill with NaNs 
        for v in var_ICON.data_vars:
            traj_vars[v] = ( ("ntraj",), [np.nan] )

        traj_ds = xr.Dataset( traj_vars, coords={'ntraj': np.arange(m)} )
        traj_ds = traj_ds.assign_coords( time=("time", [flight_time]) )
        traj_ds['lat'] = ( ["ntraj", "time"], flight_lat*np.ones((m, 1)) )
        traj_ds['lon'] = ( ["ntraj", "time"], flight_lon*np.ones((m, 1)) )
        traj_ds['alt'] = ( ["ntraj", "time"], flight_alt*np.ones((m, 1)) )
        traj_ds['pressure'] = ( ["ntraj", "time"], np.nan*np.ones((m, 1)) )

        return xr.concat([syn_traj, traj_ds], dim='time')
    
    # Construct the time window to extract.
    #early_time = flight_time_approx - datetime.timedelta(minutes=time_int)
    #late_time = flight_time_approx + datetime.timedelta(minutes=time_int)

    # Find indices corresponding to ICON pressure levels above + below the closest flight track match.
    sim_pressures = var_ICON['plev']
    i = np.argmin( np.abs(sim_pressures.values - flight_pressure) )
    #print( 'Sim-to-flight pressure difference: ' + str( (sim_pressures[i].values - flight_pressure)/100 ) + ' hPa' )
    
    # The +1 below is to ensure inclusion of the altitude level above.
    var_ICON = var_ICON.isel( plev=i )

    # Extract the time and lat-lon intervals
    var_ICON = var_ICON.sel( time=flight_time_approx,
                             lat=slice(flight_lat-ll_int, flight_lat+ll_int),
                             lon=slice(flight_lon-ll_int, flight_lon+ll_int) )

    # If there are ICON data with non-nan values along 'ntraj',
    # randomly generate <n> values and save these from the var_ICON structure into syn_traj.
    if all(var_ICON[d].shape[0] > 0 for d in var_ICON.dims):
        # Extract n_traj random values from the subset created above (only do this once not in every for iteration).
        vv = var_ICON.qv

        # Create random indices along each dimension because we need to retain the pressure values
        l1_idx = ri(0, vv.sizes['lat'], size=n_traj)
        l2_idx = ri(0, vv.sizes['lon'], size=n_traj)
        for v in var_ICON.data_vars:
            var_da = var_ICON[v]
            sampled = var_da.isel( lat=xr.DataArray(l1_idx, dims='ntraj'),
                                   lon=xr.DataArray(l2_idx, dims='ntraj') )
            traj_vars[v] = (("ntraj",), sampled.values)
    
        # Create a new 'time' dimension that only contains the single flight time.
        traj_ds = xr.Dataset( traj_vars, coords={'ntraj': np.arange(n_traj)} )
        traj_ds = traj_ds.assign_coords( time=("time", [flight_time]) )

        # Add lat, lon, and alt fields that contain the single flight lat, lon, alt.
        traj_ds['lat'] = ( ["ntraj", "time"], flight_lat*np.ones((n_traj, 1)) )
        traj_ds['lon'] = ( ["ntraj", "time"], flight_lon*np.ones((n_traj, 1)) )
        traj_ds['alt'] = ( ["ntraj", "time"], flight_alt*np.ones((n_traj, 1)) )

        # Add pressure values that were sampled
        sampled_plev = var_ICON.plev.values
        traj_ds['pressure'] = (("ntraj",), np.full(n_traj, sampled_plev))
        syn_traj = xr.concat([syn_traj, traj_ds], dim='time')
        
    # Fill with a NaN if there no longer valid ICON data along 'ntraj'
    else:
        for v in var_ICON.data_vars:
            traj_vars[v] = ( ("ntraj",), [np.nan] )

        # Create a new 'time' dimension that only contains the single flight time.
        traj_ds = xr.Dataset( traj_vars, coords={'ntraj': np.arange(m)} )
        traj_ds = traj_ds.assign_coords( time=("time", [flight_time]) )

        # Add lat, lon, and alt fields that contain the single flight lat, lon, alt.
        traj_ds['lat'] = ( ["ntraj", "time"], flight_lat*np.ones((m, 1)) )
        traj_ds['lon'] = ( ["ntraj", "time"], flight_lon*np.ones((m, 1)) )
        traj_ds['alt'] = ( ["ntraj", "time"], flight_alt*np.ones((m, 1)) )

        # Fill the pressure value with nan
        traj_ds['pressure'] = ( ["ntraj", "time"], [np.nan] )
        syn_traj = xr.concat( [syn_traj, traj_ds], dim='time' )

    return syn_traj
