# var - which group in the MLS kernels to use (e.g. "Temperature" and "H2O")
# ext_mls_start - external profile regridded to MLS RetrievedLevels
# mls_apriori - MLS profile to which we compare
def mls_regrid_kernel( var, ext_mls_start, mls_apriori ):
    import xarray as xr, numpy as np
    
    # Open the MLS averaging kernel and extract the "A matrix" mapping RetrievalLevels to TruthLevels
    bd = '/groups/sylvia/UTLS-profiles/obs/MLS/'
    ds = xr.open_dataset( bd + 'MLS_v5_1D_AVK_35N.nc4', group=var )
    A = ds.avkv.values
    mask = np.isfinite( ext_mls_start )
    # Kernels for MLS water vapor must be applied in log space, all others in linear space.
    if var == 'H2O':
        return_val = np.exp( np.log(mls_apriori) + A[:, mask] @ (np.log(ext_mls_start[mask]) - np.log(mls_apriori[mask])) )
    else:
        return_val = mls_apriori + A[:, mask] @ (ext_mls_start[mask] - mls_apriori[mask])
    return return_val