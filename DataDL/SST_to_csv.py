import xarray as xr
import pandas as pd
from netCDF4 import Dataset

try:
    ds = xr.open_dataset("../Database/SST/sst.mon.mean.nc")
    print(ds.data_vars) 
except Exception as e:
    print("⚠️ Error:", e)

print(ds.lon.min().item(), ds.lon.max().item())
print(ds.lat.min().item(), ds.lat.max().item())

print(1, ds.variables)# keys of variables in the file
# Point to the OpenDAP dataset for monthly SST

lon = 360-22
lat = 13.0

point = ds.sel(lon=lon, lat=lat, method="nearest")
print(point.lon.values, point.lat.values)
print(point.sst.values)
# Select your location; e.g., lon=10E, lat=45N
sst_point = ds.sst.sel(lon=lon, lat=lat, method="nearest")

# Convert to Pandas time series
df = sst_point.to_dataframe().reset_index()

# Save to CSV
df.to_csv(f"cobe_sst_{lon}E_{lat}N.csv", index=False)
print(df.head())
