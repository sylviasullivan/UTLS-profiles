# Calculate the mean, median, and standard deviation of variables 
# tracked along simulation trajectories in dataset ds + theta and RHi.
# bins_sim refers to the vertical bins to be used from the simulation data.
def statisticsFunc( ds, bins_sims ):

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
    theta = calc_theta( ds['temp'], ds['plev'] )
    # qv [=] kg kg-1 below
    RHi = calc_RHi( ds['temp'], ds['plev'], ds['qv'] )
    ds = ds.assign( theta=theta, RHi=RHi )

    # Define the dimension sizes
    n_bins = len(bins_sims)
    n_traj = ds.dims["ntraj"]

    # Calculate a bin index for each time-traj point
    bin_idx = xr.apply_ufunc( lambda alt: np.digitize(alt, bins_sims), ds["alt"],
                              input_core_dims=[["time"]], output_core_dims=[["time"]],
                              vectorize=True, output_dtypes=[int] )

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
            for b in np.arange(n_bins):
                mask = bin_idx.isel(ntraj=t) == b
                traj_data = data.isel(ntraj=t).where(mask)
                if traj_data.size > 0:
                    output[0, b, t] = np.nanmean(traj_data)
                    output[1, b, t] = np.nanmedian(traj_data)
                    output[2, b, t] = np.nanstd(traj_data)

        for i, stat in enumerate(stat_names):
           stats[f"{var}_{stat}"] = (["alt", "ntraj"], output[i,:,:])

    return xr.Dataset( stats, coords={"alt": bins_sims, "ntraj": np.arange(n_traj)} )
