# Input the existing syn_traj Dataset along with time, pressure, lat, and lon from the flight track
def collocateFunc( syn_traj, var_ICON, flight_time, flight_pressure, flight_lat, flight_lon, flight_alt ):
    import datetime, sys, time
    import numpy as np
    import xarray as xr
    import sys
    from timeround10 import timeround10

    # Find the closest whole 10-min time from the simulation.
    flight_time_approx = timeround10(flight_time)
    
    # Find the index corresponding to the ICON pressure level closest to that of the flight track
    sim_pressures = var_ICON['plev']
    i = np.argmin( np.abs(flight_pressure - sim_pressures.values) )

    # Find the index corresponding to the ICON lat/lon closest to that of the flight track
    lat_ICON = var_ICON.lat
    lon_ICON = var_ICON.lon
    j = np.argmin( np.abs(flight_lat - lat_ICON.values) )
    k = np.argmin( np.abs(flight_lon - lon_ICON.values) )

    # Extract the time and lat-lon intervals
    var_ICON = var_ICON.isel( plev=i, lat=j, lon=k )

    traj_vars = {}
    # Determine whether the flight time is still within the ICON outputs
    #print( flight_time_approx )
    #print( var_ICON.time.values[-1] )
    #print( type(flight_time_approx) )
    #print( type(var_ICON.time.values[-1]) )
    if np.datetime64(flight_time_approx) > var_ICON.time.values[-1]:
        for v in var_ICON.data_vars:
            traj_vars[v] = ( ("ntraj",), [np.nan])
    else:
        var_ICON = var_ICON.sel( time=flight_time_approx )
        for v in var_ICON.data_vars:
            traj_vars[v] = ( ("ntraj",), [var_ICON[v].item()])

    # Create a new 'time' dimension that only contains the single flight time.
    traj_ds = xr.Dataset( traj_vars, coords={'ntraj': [0]} )
    traj_ds = traj_ds.assign_coords( time=("time", [flight_time]) )

    # Add lat, lon, and alt fields that contain the single flight lat, lon, atl.
    traj_ds['lat'] = ( ["ntraj", "time"], [[flight_lat]] )
    traj_ds['lon'] = ( ["ntraj", "time"], [[flight_lon]] )
    traj_ds['alt'] = ( ["ntraj", "time"], [[flight_alt]] )
    traj_ds['plev'] = ( ["ntraj", "time"], [[flight_pressure]] )
    syn_traj = xr.concat( [syn_traj, traj_ds], dim='time' )

    return syn_traj