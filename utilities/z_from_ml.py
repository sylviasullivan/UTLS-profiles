def z_from_ml(lat_in,lon_in):
    from scipy.interpolate import UnivariateSpline
    import xarray as xr
    import numpy as np

    # This set of output used full levels.
    #half_levels = np.arange(91)
    #half_level_heights = np.asarray([75000,72363,69842,67357,64946,62606,60336,58132,\
    # 55976,53877,51824,49826,47890,46014,44197,42438,40736,39089,37497,35958,34472,\
    # 33038,31655,30322,29038,27803,26617,25488,24416,23408,22460,21569,20731,\
    # 19942,19201,18504,17849,17232,16653,16108,15595,15113,14660,14234,13821,\
    # 13421,13021,12621,12221,11821,11421,11021,10621,10221,9821,9421,9021,8621,\
    # 8221,7821,7421,7021,6621,6221,5821,5421,5033,4659,4300,3954,3622,3303,2999,\
    # 2708,2431,2168,1919,1683,1462,1255,1062,883,719,570,436,318,216,131,65,20,0])

    #full_levels = np.arange(90)   # There should be 90 full levels and 91 half levels.
    #full_level_heights = np.asarray([73681,71102,68600,66152,63775,61470,59233,57054,\
    #  54927,52851,50825,48858,46952,45106,43318,41587,39912,38293,36727,35215,33755,\
    #  32346,30988,29680,28421,27210,26053,24952,23912,22934,22015,21150,20336,19572,\
    #  18853,18176,17540,16942,16380,15851,15354,14886,14447,14027,13621,13221,12821,\
    #  12421,12021,11621,11221,10821,10421,10021,9621,9221,8821,8421,8021,7621,7221,\
    #  6821,6421,6021,5621,5227,4846,4480,4127,3788,3462,3151,2853,2570,2300,2043,\
    #  1801,1573,1358,1158,972,801,644,503,377,267,174,98,42,10])

    # top_height parameter in run_TROPIC.run was 30 km.
    full_level_heights = np.asarray([30988,29680,28421,27210,26053,24952,23912,22934,\
      22015,21150,20336,19572,18853,18176,17540,16942,16380,15851,15354,14886,14447,\
      14027,13621,13221,12821,12421,12021,11621,11221,10821,10421,10021,9621,9221,\
      8821,8421,8021,7621,7221,6821,6421,6021,5621,5227,4846,4480,4127,3788,3462,3151,\
      2853,2570,2300,2043,1801,1573,1358,1158,972,801,644,503,377,267,174,98,42,10])

    # Read in the topography at 0.025 lat / lon grid.
    #basedir = '/work/bb1018/b380459/TROPIC/extpar/'
    #extpar_unstructured = basedir + 'extpar_icon-grid_tropic_55e170e5s40n_R2500m_bitmap.nc'
    basedir = '/work/bb1018/b380873/tropic_run2_output/'
    extpar_latlon = basedir + 'extpar_icon-grid_tropic_55e170e5s40n_R2500m_bitmap_remapdis0.025.nc'
    xp = xr.open_dataset(extpar_latlon)
    topography = xp.topography_c
    lat = xp.lat
    lon = xp.lon

    # Find the indices corresponding to the input latitude and longitude.
    res = np.abs(lat - lat_in).argmin()
    reslat = np.unravel_index(res,lat.shape)[0]
    res = np.abs(lon - lon_in).argmin()
    reslon = np.unravel_index(res,lon.shape)[0]

    # Extract the topography at that lat and lon.
    topo_latlon = topography[reslat,reslon]

    # Add this topography to the array of full levels and return the profile.
    zprofile = full_level_heights + topo_latlon.values
    old_indices = np.arange(len(zprofile))
    new_length = 90
    new_indices = np.linspace(0,len(zprofile)-1,new_length)
    spl = UnivariateSpline(old_indices,zprofile,k=3,s=0)
    zprofile_90 = spl(new_indices)
    return zprofile_90
