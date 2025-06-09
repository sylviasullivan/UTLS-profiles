import numpy as np
import xarray as xr
import sys, time
import pandas as pd
import datetime
from collocateSim import collocateSim

# Global variables in the script form
sim_acronym = '0V2M1A1R'
n = 1

# Load the observational data
basedir = '/work/bb1018/b380873/tropic_vis/obs/'
fi = basedir + 'stratoclim2017.geophysika.0808_1.filtered_per_sec.nc'
Stratoclim = xr.open_dataset(fi)
flight_times = Stratoclim['time']

# <j> is the first iteration for which there are ICON high-resolution values available.
j = 1942 # 1342
#tt = flight_times.shape[0] - j
tt = 0

# Load the ICON values
ICON = xr.open_dataset('/work/bb1018/b380873/model_output/ICON/ICON_3D_F10MIN_icon_tropic_' + sim_acronym + '_PL2.nc')

# Initiate the synthetic trajectory Dataset
syn_traj = xr.Dataset( data_vars=dict(
                            omega=( ["time", "ntraj"], np.zeros([tt, n], dtype=np.float32) ),
                            temp=( ["time", "ntraj"], np.zeros([tt, n], dtype=np.float32) ),
                            air_pressure=( ["time", "ntraj"], np.zeros([tt, n], dtype=np.float32) ),
                            qv=( ["time", "ntraj"], np.zeros([tt, n], dtype=np.float32) ),
                            qi=( ["time", "ntraj"], np.zeros([tt, n], dtype=np.float32) ),
                            qc=( ["time", "ntraj"], np.zeros([tt, n], dtype=np.float32) ),
                            qs=( ["time", "ntraj"], np.zeros([tt, n], dtype=np.float32) ),
                            qg=( ["time", "ntraj"], np.zeros([tt, n], dtype=np.float32) ),
                            clc=( ["time", "ntraj"], np.zeros([tt, n], dtype=np.float32) ),
                            lat=( ["time", "ntraj"], np.zeros([tt, n], dtype=np.float64) ),
                            lon=( ["time", "ntraj"], np.zeros([tt, n], dtype=np.float64) ),
                            alt=( ["time", "ntraj"], np.zeros([tt, n], dtype=np.float64) ),
                        ),
                       coords=dict( time=[], ntraj=np.arange(1, 2) ) #time=flight_times[j:]
                     )

# Set the variable attributes as in the standard ICON output file.
for v in syn_traj.data_vars:
    syn_traj[v] = np.nan
    if v != 'alt':
        syn_traj[v].attrs["long_name"] = ICON[v].long_name
        syn_traj[v].attrs["units"] = ICON[v].units
        syn_traj[v].attrs["standard_name"] = ICON[v].standard_name
    else:
        syn_traj[v].attrs["long_name"] = "Altitude"
        syn_traj[v].attrs["units"] = "m"

for flight_iter, flight_time in enumerate(flight_times[j:]):
    if flight_iter%100 == 0:
        print(flight_iter)

    # timestamp-datetime-timedoodadoo conversion from hell....
    flight_time_not_np = pd.to_datetime(flight_time.values).to_pydatetime()
    flight_pressure = Stratoclim['BEST:PRESS'].sel(time=flight_time_not_np).values*100 # [Pa]
    flight_lat = Stratoclim['BEST:LAT'].sel(time=flight_time_not_np).values
    flight_lon = Stratoclim['BEST:LON'].sel(time=flight_time_not_np).values
    flight_alt = Stratoclim['BEST:ALT'].sel(time=flight_time_not_np).values

    # Based on the flight values, load the relevant chunk of simulations
    syn_traj = collocateSim(syn_traj, ICON, flight_time_not_np, flight_pressure, flight_lat, flight_lon, flight_alt)

syn_traj.transpose("time", "ntraj")
syn_traj.to_netcdf(path='/work/bb1018/b380873/model_output/ICON/ICON_synthetic_trajs_' + sim_acronym + '_C.nc')
