# Calculate the mean, median, and standard deviation of variables 
# tracked along simulation trajectories in dataset ds + theta and RHi.
# plevs refers to the pressure bins to be used from the simulation data.
def statisticsFunc( ds, plevs ):

    import numpy as np
    import warnings, time
    import xarray as xr
    import time, sys, os
    sys.path.append(os.path.abspath("/groups/sylvia/UTLS-profiles/utilities/"))
    from thermodynamic_functions import calc_RHi, calc_theta

    warnings.filterwarnings("ignore", message="All-NaN slice encountered")
    warnings.filterwarnings("ignore", message="Mean of empty slice")
    warnings.filterwarnings("ignore", message="Degrees of freedom <= 0 for slice")

    # Calculate derived variables
    theta = calc_theta( ds['temp'], ds['pressure'] )
    # qv [=] kg kg-1 below
    RHi = calc_RHi( ds['temp'], ds['pressure'], ds['qv'] )
    ds = ds.assign( theta=theta, RHi=RHi )

    # Define the dimension sizes
    n_bins = len(plevs)
    n_traj = ds.dims["ntraj"]

    # Calculate a bin index for each time-traj point
    pressure_vals = ds.pressure.values
    bin_idx = np.empty_like(pressure_vals, dtype=int)
    for i in range(pressure_vals.shape[0]):
        for j in range(pressure_vals.shape[1]):
            val = pressure_vals[i,j]
            ii = np.argmin(np.abs(plevs - val))
            bin_idx[i,j] = ii

    # Constants needed for mixing ratio conversion
    mw_dryair = 28.97*1000    # kg air (mol air)-1
    mw_watvap = 18.02*1000    # kg wv (mol wv)-1
    conv = mw_dryair / mw_watvap
    
    # Preallocate output
    stats = {}
    stat_names = ["mean", "median", "std"]
    for var in ds.data_vars:
        print( var )
        
        # Convert mixing ratios from kg kg-1 to ppmv
        if var == 'qv' or var == 'qi' or var == 'qs':
            ds[var] = ds[var] * conv * 10**6
        data = ds[var]
        output = np.full((3, n_bins, n_traj), np.nan)

        for t in np.arange(n_traj):
            for b in np.arange(len(plevs)):
                mask = bin_idx[:,t] == b
                traj_data = data.isel(ntraj=t).where(mask)
                if traj_data.size > 0:
                    output[0, b, t] = np.nanmean(traj_data)
                    output[1, b, t] = np.nanmedian(traj_data)
                    output[2, b, t] = np.nanstd(traj_data)

        for i, stat in enumerate(stat_names):
           stats[f"{var}_{stat}"] = (["pressure", "ntraj"], output[i,:,:])

    return xr.Dataset( stats, coords={"pressure": plevs, "ntraj": np.arange(n_traj)} )
