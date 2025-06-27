import numpy as np
import xarray as xr
import sys, time
import pandas as pd
import datetime
from extractFunc import extractFunc

# Run this driver like python extractDriver.py <sim_acronym> (e.g., python extractDriver.py 1M0O)
sim_acronym = sys.argv[1]

# Parameters that can be varied (number of trajectories; lat/lon, altitude, and time interval sizes)
n_traj = 20
ll_int = 0.25  # [+/- degrees from flight location]
alt_int = 1    # [+/- number of altitudinal levels from flight location]
time_int = 10  # [+/- minutes from flight time]

# Load the ICON and flight track values
bd1 = '/xdisk/sylvia/UTLS_flight_output/'
ICON = xr.open_dataset(bd1 + sim_acronym + '/ICON_3D_flight_' + sim_acronym + '.nc')
bd2 = '/groups/sylvia/UTLS-profiles/obs/'
Stratoclim = xr.open_dataset( bd2 + 'stratoclim2017.geophysika.0808_1.filtered_per_sec.nc' )
flight_times = Stratoclim['time']

# Initiate the synthetic trajectory Dataset with no time entries. 
# These will be added sequentially, iterating through the flight track times.
data_vars = {}
for v in ICON.data_vars:
    data_vars[v] = ( ["time","ntraj"], np.empty((0, n_traj )) )
data_vars['lat'] = ( ["time","ntraj"], np.empty((0, n_traj )) )
data_vars['lon'] = ( ["time","ntraj"], np.empty((0, n_traj )) )
data_vars['alt'] = ( ["time","ntraj"], np.empty((0, n_traj )) )

syn_traj = xr.Dataset(  data_vars=data_vars, coords=dict( time=np.empty((0,), dtype='datetime64[ns]' ),
                         ntraj=np.arange(0, n_traj) ) ) #1,n_traj+1

# Set the variable attributes for the synthetic trajectories as in the standard ICON output file.
for v in syn_traj.data_vars:
    if v != 'alt':
       syn_traj[v].attrs["long_name"] = ICON[v].long_name
       syn_traj[v].attrs["units"] = ICON[v].units
       syn_traj[v].attrs["standard_name"] = ICON[v].standard_name
    else:
       syn_traj[v].attrs["long_name"] = "Altitude"
       syn_traj[v].attrs["units"] = "m"

syn_traj['ntraj'].attrs["long_name"] = 'Trajectory ID'

for flight_iter, flight_time in enumerate(flight_times):
    if flight_iter%500 == 0:
       print(flight_iter)

    # timestamp-datetime conversion and extraction of relevant flight values
    flight_time_not_np = pd.to_datetime(flight_time.values).to_pydatetime()
    flight_pressure = Stratoclim['BEST:PRESS'].sel(time=flight_time_not_np).values*100 # [Pa]
    flight_lat = Stratoclim['BEST:LAT'].sel(time=flight_time_not_np).values
    flight_lon = Stratoclim['BEST:LON'].sel(time=flight_time_not_np).values
    flight_alt = Stratoclim['BEST:ALT'].sel(time=flight_time_not_np).values

    # Based on the flight values, load the relevant chunk of simulations
    syn_traj = extractFunc( syn_traj, ICON, flight_time_not_np, flight_pressure, flight_lat, flight_lon, flight_alt, n_traj, ll_int, alt_int, time_int )

syn_traj.to_netcdf(path='/groups/sylvia/UTLS-profiles/output/ICON_synthetic_trajs_' + sim_acronym + '_E.nc')
