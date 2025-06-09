# Input the existing syn_traj Dataset along with time, pressure, lat, and lon from the flight track
#@profile
def extractSim(syn_traj, var_ICON, flight_time, flight_pressure, flight_lat, flight_lon, flight_alt):
    import datetime, sys
    import numpy as np
    import xarray as xr
    from timeround10 import timeround10
    ri = np.random.randint

    # Global variables in the script form
    n = 20
    ll_interval = 0.5
    alt_interval = 1

    # Find the nearest whole 10-min time.
    flight_time_approx = timeround10(flight_time)

    # Construct the time window to extract.
    early_time = flight_time_approx - datetime.timedelta(minutes=30)
    late_time = flight_time_approx + datetime.timedelta(minutes=30)

    # Find indices corresponding to ICON pressure levels above + below the closest flight track match.
    basedir = '/groups/sylvia/UTLS-profiles/'
    sim_pressures = np.loadtxt(basedir + 'PMEAN_48-72.txt')
    i = np.argmin(np.abs(flight_pressure - sim_pressures))
    print('central index in plev to be used: ' + str(i))
    if i < 1 or i > 117:
        raise Exception('Flight pressure outside of simulation range.')
    var_ICON = var_ICON.isel( plev=slice(i-alt_interval, i+alt_interval+1) )

    # Extract the time and lat-lon intervals
    ## sylvia_20250604 - work around below to just generate trajectories, to be removed after sim output update
    var_ICON['time'] = var_ICON['time'] - np.timedelta64(1,'D') 
    var_ICON = var_ICON.sel( time=slice(early_time, late_time),
                             lat=slice(flight_lat-ll_interval, flight_lat+ll_interval),
                             lon=slice(flight_lon-ll_interval, flight_lon+ll_interval) )

    # Randomly generate <n> indices along each axis and save these from the var_ICON structure into syn_traj.
    nt = var_ICON.dims['time']
    nlat = var_ICON.dims['lat']
    nlon = var_ICON.dims['lon']
    nplev = var_ICON.dims['plev']
    
    print(var_ICON['plev'])
    print(nplev)
    time_indices = np.random.randint(0, nt, size=n)
    lat_indices = np.random.randint(0, nlat, size=n)
    lon_indices = np.random.randint(0, nlon, size=n)
    plev_indices = np.random.randint(0, nplev, size=n)
    print(plev_indices)

    # Merge the lat, lon, plev, and time dimensions into a new 'ntraj' dimension.
    traj_vars = {}
    for v in var_ICON.data_vars:
        var_da = var_ICON[v].values
        sampled = var_da[time_indices,plev_indices,lat_indices,lon_indices]
        traj_vars[v] = (("ntraj",), sampled.flatten())
    
    # Create a new 'time' dimension that only contains the single flight time.
    traj_ds = xr.Dataset(traj_vars, coords={'ntraj': np.arange(len(time_indices))})
    traj_ds = traj_ds.assign_coords(time=("time", [flight_time]))  #.expand_dims("time")

    # Add lat, lon, and alt fields to guy that contain the single flight lat, lon, alt.
    traj_ds['lat'] = (["ntraj", "time"], flight_lat*np.ones((n, 1)))
    traj_ds['lon'] = (["ntraj", "time"], flight_lon*np.ones((n, 1)))
    traj_ds['alt'] = (["ntraj", "time"], flight_alt*np.ones((n, 1)))
    syn_traj = xr.concat([syn_traj, traj_ds], dim='time')
    return syn_traj

#profilewrapper()
