# Input the existing syn_traj Dataset along with time, pressure, lat, and lon from the flight track
def extractFunc( syn_traj, var_ICON, flight_time, flight_pressure, flight_lat, flight_lon, flight_alt, n_traj, ll_int, alt_int, time_int ):
    import datetime, sys
    import numpy as np
    import xarray as xr
    import sys
    from timeround10 import timeround10
    ri = np.random.randint

    # Find the nearest whole 10-min time.
    flight_time_approx = timeround10(flight_time)

    # Construct the time window to extract.
    early_time = flight_time_approx - datetime.timedelta(minutes=time_int)
    late_time = flight_time_approx + datetime.timedelta(minutes=time_int)

    # Find indices corresponding to ICON pressure levels above + below the closest flight track match.
    bd = '/groups/sylvia/UTLS-profiles/'
    sim_pressures = var_ICON['plev']
    i = np.argmin( np.abs(flight_pressure - sim_pressures.values) )
    #print( 'Sim-to-flight pressure difference: ' + str( (sim_pressures[i].values - flight_pressure)/100 ) + ' hPa' )
    
    # The +1 below is to ensure inclusion of the altitude level above.
    var_ICON = var_ICON.isel( plev=slice(i-alt_int, i+alt_int+1) )

    # Extract the time and lat-lon intervals
    var_ICON = var_ICON.sel( time=slice(early_time, late_time),
                             lat=slice(flight_lat-ll_int, flight_lat+ll_int),
                             lon=slice(flight_lon-ll_int, flight_lon+ll_int) )

    # Randomly generate <n> indices along each axis and save these from the var_ICON structure into syn_traj.
    # Merge the lat, lon, plev, and time dimensions into a new 'ntraj' dimension.
    traj_vars = {}
    m = 1

    # If there are ICON data with non-nan values along 'ntraj'
    if all(var_ICON[d].shape[0] > 0 for d in var_ICON.dims):
        # Extract n_traj random values from the subset created above.
        for v in var_ICON.data_vars:
            var_da = var_ICON[v].values.flatten()
            idx = ri( 0, var_da.shape[0], size=n_traj )
            sampled = var_da[idx]
            traj_vars[v] = (("ntraj",), sampled)
    
        # Create a new 'time' dimension that only contains the single flight time.
        traj_ds = xr.Dataset( traj_vars, coords={'ntraj': np.arange(n_traj)} )
        traj_ds = traj_ds.assign_coords( time=("time", [flight_time]) )

        # Add lat, lon, and alt fields that contain the single flight lat, lon, alt.
        traj_ds['lat'] = ( ["ntraj", "time"], flight_lat*np.ones((n_traj, 1)) )
        traj_ds['lon'] = ( ["ntraj", "time"], flight_lon*np.ones((n_traj, 1)) )
        traj_ds['alt'] = ( ["ntraj", "time"], flight_alt*np.ones((n_traj, 1)) )
        traj_ds['plev'] = ( ["ntraj", "time"], flight_pressure*np.ones((n_traj, 1)) )
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
        traj_ds['plev'] = ( ["ntraj", "time"], flight_pressure*np.ones((m, 1)) )
        syn_traj = xr.concat( [syn_traj, traj_ds], dim='time' )

    return syn_traj
