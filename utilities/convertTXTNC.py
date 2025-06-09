from netCDF4 import Dataset
import numpy as np

pi = 3.14159265358979323846264338

# List of lats and lons read in from txt file.
with open('icon-grid_tropic_55e115e5s40n_R2500m_lats.txt') as f:
     lats_ws = f.read().splitlines()
lat_vals = np.array([float(ll) for line in lats_ws for ll in line.split()])
lat_vals_deg = np.array([float(ll)*180/pi for line in lats_ws for ll in line.split()])

with open('icon-grid_tropic_55e115e5s40n_R2500m_lons.txt') as f:
     lons_ws = f.read().splitlines()
lon_vals = np.array([float(ll) for line in lons_ws for ll in line.split()])
lon_vals_deg = np.array([float(ll)*180/pi for line in lons_ws for ll in line.split()])

# Sanity check - print the min-max lat-lon bounds.
minlat = np.nanmin(lat_vals_deg)
maxlat = np.nanmax(lat_vals_deg)
minlon = np.nanmin(lon_vals_deg)
maxlon = np.nanmax(lon_vals_deg)
print('Min, max lat: ' + str(minlat) + ' ' + str(maxlat))
print('Min, max lon: ' + str(minlon) + ' ' + str(maxlon))

# Generate a netcdf file to hold these values.
gridnc = Dataset('icon-gridcell_latlon_55e115e5s40n.nc','w',format='NETCDF4')
ncell = gridnc.createDimension('ncell',lon_vals.shape[0])

gridcell = gridnc.createVariable('gridcell',np.int,('ncell'))
gridcell[:] = np.arange(lon_vals.shape[0])
gridcell.long_name = "Gridcell number"

lats = gridnc.createVariable('latitude',np.float32,('ncell'))
lats[:] = lat_vals
lats.long_name = "Latitude"
lats.units = "radians"

lats_deg = gridnc.createVariable('latitude_deg',np.float32,('ncell'))
lats_deg[:] = lat_vals_deg
lats_deg.long_name = "Latitude"
lats_deg.units = "degree"

lons = gridnc.createVariable('longitude',np.float32,('ncell'))
lons[:] = lon_vals
lons.long_name = "Longitude"
lons.units = "radians"

lons_deg = gridnc.createVariable('longitude_deg',np.float32,('ncell'))
lons_deg[:] = lon_vals_deg
lons_deg.long_name = "Longitude"
lons_deg.units = "degree"

gridnc.close()
