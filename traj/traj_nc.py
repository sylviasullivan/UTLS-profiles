import numpy as np
import xarray as xr
import netCDF4
import glob, time

# Where are the trajectory files sitting?
#basedir = '/work/bb1018/b380873/traj_output/test24h/'
basedir = '/work/bb1018/b380873/traj_output/traj_ICON_0V2M0A0R/'
#basedir = '/scratch/b/b380873/traj_0V1M0A0R/'

# Timesteps with trajectory output
dt = ['450'] # ['450'] ['151','601','751','901']
fi_list = []
for t in dt:
    fi_list += glob.glob(basedir + 'traj_tst00000' + t + '_p*.nc')

if 'test' in basedir:
   vunits = ['','rad','rad','m','m s-1','kg m-3','K','Pa','kg kg-1','kg kg-1','kg-1','kg kg-1','kg-1','kg kg-1',\
             'kg-1','kg kg-1','kg-1','kg kg-1','kg-1','','s']
   lname = ['trajectory index','deg longitude E','deg latitude N','altitude','vertical velocity',\
            'air density','air temperature','air pressure','vapor mass mixing ratio','ice mass mixing ratio',\
            'ice crystal number conc','liquid water mass mixing ratio','cloud droplet number conc',\
            'snow mass mixing ratio','snow number conc','rain mass mixing ratio','rain drop number conc',\
            'graupel mass mixing ratio','graupel number conc','grid cell index','time after the simulation start']
else:
   vunits = ['','rad','rad','m','m s-1','kg m-3','K','Pa','kg kg-1','kg kg-1','kg-1','kg kg-1','kg-1','kg kg-1',\
             'kg-1','kg kg-1','kg-1','kg kg-1','kg-1','kg-1','kg-1','kg kg-1','kg kg-1','','s']
   lname = ['trajectory index','deg longitude E','deg latitude N','altitude','vertical velocity',\
            'air density','air temperature','air pressure','vapor mass mixing ratio','ice mass mixing ratio',\
            'ice crystal number conc','liquid water mass mixing ratio','cloud droplet number conc',\
            'snow mass mixing ratio','snow number conc','rain mass mixing ratio','rain drop number conc',\
            'graupel mass mixing ratio','graupel number conc','ice sedimentation mass flux in',\
            'ice sedimentation mass flux out','ice sedimentation number flux in','ice sedimentation number flux out',\
            'grid cell index','time after the simulation start']

for f in fi_list:
    # Take the patch 1 file as a sample
    print(f)
    fi = xr.open_dataset(f)
    # Find indices where the grid != 0.
    xs, ys = np.where(fi.alt.values != 0)
    print('time: ' + str(max(xs)) + ' id: ' + str(max(ys)) + ' (assuming dims are not switched)')

    # Crop all files according to the xs and ys indices.
    fi2 = xr.Dataset()       # updated Dataset
    for i, v in enumerate(fi.data_vars):
        print(v)
        if str(v) != 'rtime':
           # When the dimensions were backwards, time and id needed to be switched below.
           v1 = fi[v].isel(time=np.arange(max(xs)+1),id=np.arange(max(ys)+1))
           v1.attrs['units'] = vunits[i]
           v1.attrs['long_name'] = lname[i]
           # When the dimensions were backwards, the following was needed.
           #v1 = v1.rename({'time': 'traj_id','id': 'time_step'})
           fi2[str(v)] = v1
        else:
           v1 = fi[v].isel(time=np.arange(max(xs)+1))
           v1.attrs['units'] = vunits[i]
           v1.attrs['long_name'] = lname[i]
           # When the dimensions were backwards, the following was needed.
           #v1 = v1.rename({'time': 'time_step'})
           fi2[str(v)] = v1

    fi2.to_netcdf(f[:-3] + '_trim.nc')
    print('Saving ' + f[:-3] + '_trim.nc')

