#!/usr/bin/env python

###### This script will calculate PCs at a given time based on the two leading ERA5 EOF patterns that describe
###### the variability of the North Pacific jet stream during the cool season. Input data must be daily or monthly resolution and
###### regridded onto a 1x1 degree grid first. Outputs include the frequency of each NPJ regime and a timeseries of PCs.

import sys
import os
import json
import platform
import logging
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.pyplot import get_cmap
import numpy as np
import xarray as xr
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
from datetime import datetime, timezone

#####################################################################################
########################### Define functions ########################################
#####################################################################################
def get_package_versions():
    """Return versions of key python packages."""
    versions = {}
    versions["numpy"] = np.__version__
    versions["xarray"] = xr.__version__
    versions["matplotlib"] = matplotlib.__version__
    versions["cartopy"] = cartopy.__version__
    versions["python"] = platform.python_version()
    return versions

def write_json(data,filename):
    """Create a new JSON file.
    Args:
        data (dictionary): data to write
        filename (str): output file name
    """
    with open(filename, "w") as outfile:
        json.dump(data, outfile, indent=4)

#####################################################################################
########################### Initialize variables ####################################
#####################################################################################

# Get CMEC environment variables
#input_data_path = "/global/homes/a/awinters/NPJphase/input_files"
#output_data_path = "/global/homes/a/awinters/NPJphase/output_files"
#climo_data_path = "/global/homes/a/awinters/NPJphase"

input_data_path = os.getenv("CMEC_MODEL_DATA")
output_data_path = os.getenv("CMEC_WK_DIR")
climo_data_path = os.getenv("CMEC_CODE_DIR")

log_file = "npjphase.log"
log_file_name = os.path.join(output_data_path, log_file)
logging.basicConfig(filename=str(log_file_name), encoding="utf-8", level=logging.INFO)

############################ Get user settings from cmec interface ######################
user_settings_json = os.path.expandvars('$CMEC_CONFIG_DIR/cmec.json')
#user_settings_json = os.path.expandvars('/global/homes/a/awinters/.cmec/cmec.json')
try:
    with open(user_settings_json) as config_file:
        user_settings = json.load(config_file).get("NPJphase")
    # Get any environment variables and check settings type
    for setting in user_settings:
        if isinstance(user_settings[setting], str):
            user_settings[setting] = os.path.expandvars(user_settings[setting])
    # User settings to global variables
    globals().update(user_settings)
except json.decoder.JSONDecodeError:
    print("*** Could not load settings from " + str(user_settings_json) + ". File may not be valid JSON. ***\n")

### Domain bounds over the N. Pacific Basin
latS = 10.5    
latN = 79.5
lonW = 100.5 
lonE = 239.5  

plev = pressure_level
datafreq = frequency    
model = data_type
input_file = input_dataset

logging.info("Requested pressure level: "+plev+" hPa")
logging.info("Requested temporal frequency: "+datafreq)
logging.info("Model data type: "+model)

#####################################################################################
############################ Read in ERA5 EOF patterns/mean wind ####################
#####################################################################################
eof_file = "climo_files/ERA5_u"+plev+"_eofs_"+datafreq+".nc"
data_path = os.path.join(climo_data_path, eof_file)
ds_eofs = xr.open_dataset(data_path)
ds_eofs = ds_eofs.reindex(lat=list(reversed(ds_eofs.lat)))
eof1 = ds_eofs.eof1
eof2 = ds_eofs.eof2
lats = ds_eofs.lat
lons = ds_eofs.lon
lons_eof, lats_eof = np.meshgrid(lons,lats)

#### initialize eigenvalues
if plev == '200':
    if datafreq == 'daily':
        eig1 = 121178.23379701
        eig2 = 97216.89832252
    if datafreq == 'month':
        eig1 = 50491.47848352
        eig2 = 41038.06904092
if plev == '250':
    if datafreq == 'daily':
        eig1 = 133385.90053738
        eig2 = 99895.74318987
    if datafreq == 'month':
        eig1 = 55570.5391435
        eig2 = 40688.78001363
if plev == '300':
    if datafreq == 'daily':
        eig1 = 124630.97984526
        eig2 = 91387.50317074
    if datafreq == 'month':
        eig1 = 52714.31104608
        eig2 = 36902.07250512

#### Read in ERA5 mean file ####
climo_file = "climo_files/climo_u"+plev+"_"+datafreq+"_mean.nc"
mean_path = os.path.join(climo_data_path, climo_file)
ds_mean = xr.open_dataset(mean_path) #,decode_times=False)
ds_mean = ds_mean.reindex(lat=list(reversed(ds_mean.lat)))
umean = ds_mean.u.sel(lat=slice(latS,latN,2),lon=slice(lonW,lonE,2))
season_mean = np.mean(umean,axis=0)

#####################################################################################
################## Read in Input Dataset ############################################
#####################################################################################
pctimes = []
regimenames = []
if datafreq == 'daily':
    pcs = np.zeros((273,3))
    totiter = 365
    may31 = 150
    sep01 = 243
if datafreq == 'month':
    pcs = np.zeros((9,3))
    totiter = 12
    may31 = 4
    sep01 = 8
npjreg = np.array([0,0,0,0,0])

#### E3SM Data
if model == 'e3sm':
    data_path = os.path.join(input_data_path, input_dataset)   ## input file name
    logging.info("Input data file: "+data_path)
    ds_e3sm = xr.open_dataset(data_path)
    if plev == '200':
        u_data = ds_e3sm.U200.sel(lat=slice(latS,latN),lon=slice(lonW,lonE))
    if plev == '250':
        u_data = ds_e3sm.U250.sel(lat=slice(latS,latN),lon=slice(lonW,lonE))
    if plev == '300':
        u_data = ds_e3sm.U300.sel(lat=slice(latS,latN),lon=slice(lonW,lonE))
    times = ds_e3sm.time
    
if model == 'era5':
    data_path = os.path.join(input_data_path, input_dataset)   ## input file name
    logging.info("Input data file: "+data_path)
    ds_era5 = xr.open_dataset(data_path)
    ds_era5 = ds_era5.reindex(latitude=list(reversed(ds_era5.latitude)))
    u_data = ds_era5.u.sel(pressure_level=int(plev),latitude=slice(latS,latN,4),longitude=slice(lonW,lonE,4))
    times = ds_era5.valid_time

if model == 'other':
    data_path = os.path.join(input_data_path, input_dataset)   ## input file name
    logging.info("Input data file: "+data_path)
    ds_other = xr.open_dataset(data_path, decode_times=False)
    u_data = ds_other.u.sel(level=int(plev),lat=slice(latS,latN),lon=slice(lonW,lonE))
    times = ds_other.time

#####################################################################################
################## Calculate PCs ####################################################
#####################################################################################
logging.info("Calculating Principal Components")
count = 0
for d in range(totiter):
    if (d <= may31) or (d >= sep01):
        upert = u_data[d,:,:].values - umean[count,:,:].values   ### calculate perturbation relative to ERA5 climatology 
        coswgt = np.cos(lats_eof[:,:]*np.pi/180.)  ### calculate cosine weights
        upertwgt = upert[:,:]*coswgt[:,:]          ### Weight data by cos(lat)
        
        upert_1D = upertwgt.flatten()       ### flatten perturbation winds to 1D array
        eof1_1D = eof1.values.flatten()            ### flatten EOF1 to 1D array           
        eof2_1D = eof2.values.flatten()            ### flatten EOF2 to 1D array

        eof1_1D = eof1_1D[:]/(np.sqrt(eig1))    ### divide eof1 by the sqrt(eigenvalue)
        eof2_1D = eof2_1D[:]/(np.sqrt(eig2))     ### divide eof2 by the sqrt(eigenvalue)
        
        sumpc1 = upert_1D[:]*eof1_1D[:]            ### project perturbation winds onto EOF1
        sumpc2 = upert_1D[:]*eof2_1D[:]            ### project perturbation winds onto EOF2
        
        pc1 = sum(sumpc1)/np.sqrt(eig1)      ### calculate PC1 by dividing by sqrt(eigenvalue)
        pc2 = sum(sumpc2)/np.sqrt(eig2)       ### calculate PC2 by dividing by sqrt(eigenvalue)

        #### Classify the NPJ regime
        if (pc1**2 + pc2**2 >= 1.0) and (pc1 > 0) and (abs(pc2) < pc1):  #Jet Extension
            regime = 1   ## jet extension
            regimename = 'extension'
  
        if (pc1**2 + pc2**2 >= 1.0) and (pc1 < 0) and (abs(pc2) < abs(pc1)): #Jet Retraction
            regime = 2   ## jet retraction
            regimename = 'retraction'
    
        if (pc1**2 + pc2**2 >= 1.0) and (pc2 > 0) and (abs(pc1) < pc2): #Poleward Shift
            regime = 3   ## poleward shift
            regimename = 'poleward shift'

        if (pc1**2 + pc2**2 >= 1.0) and (pc2 < 0) and (abs(pc1) < abs(pc2)): #Equatorward Shift
            regime = 4   ## equatorward shift
            regimename = 'equatorward shift'
 
        if (pc1**2 + pc2**2 < 1.0):
            regime = 5   ## origin
            regimename = 'origin'
        
        pctimes.append(str(times[d].values))
        pcs[count,0] = pc1
        pcs[count,1] = pc2
        regimenames.append(regimename)
        npjreg[regime-1] = npjreg[regime-1] + 1
        count = count + 1

################### Save PC data to textfile ##############################
pcfilename = 'npjpcs_'+plev+'hpa_'+datafreq+'.txt'
output_path = os.path.join(output_data_path, pcfilename)
with open(output_path, 'w') as file:
    file.write("Time, PC 1, PC 2, NPJ regime\n")
    for p in range(len(pcs)):
        file.write(pctimes[p]+","+str(pcs[p,0])+","+str(pcs[p,1])+","+regimenames[p]+"\n")

#####################################################################################
################## Create Figures ###################################################
#####################################################################################
logging.info("Creating Figures")
#################### Figure 1: Create plot of ERA5 EOF1 patterns #######################
mapcrs = ccrs.PlateCarree(central_longitude=180)

# Start the figure and create plot axes with proper projection
fig = plt.figure(1, figsize=(20, 14))
ax = plt.subplot(111, projection=mapcrs)
ax.set_extent([100, 240, 10, 80], ccrs.PlateCarree())   

# Add geopolitical boundaries for map reference
ax.add_feature(cfeature.LAND, facecolor="#bdbdbd")
countries = NaturalEarthFeature(category="cultural", scale="110m", facecolor="none", name="admin_0_boundary_lines_land")
ax.add_feature(countries, linewidth=0.5, edgecolor="black")
ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)
ax.coastlines('50m', linewidth=0.8)

# Set up contour and fill intervals
eof_levels = [-16,-14,-12,-10,-8,-6,-4,-2,2,4,6,8,10,12,14,16]
uwnd_levels = np.arange(30,65,5)
lat_levels = np.arange(20,80,20)
lon_levels = np.arange(100,240,20)

# Plot the variables
eof_fcontours = plt.contourf(lons_eof, lats_eof, eof1, levels=eof_levels, cmap=get_cmap('RdBu_r'), alpha=1, transform=ccrs.PlateCarree(),transform_first=True)
lon_contours = plt.contour(lons_eof, lats_eof, lons_eof, levels=lon_levels, colors="grey", linewidths=1, linestyles='dashed', transform=ccrs.PlateCarree())
lat_contours = plt.contour(lons_eof, lats_eof, lats_eof, levels=lat_levels, colors="grey", linewidths=1, linestyles='dashed', transform=ccrs.PlateCarree())
uwnd_contours = plt.contour(lons_eof, lats_eof, season_mean, levels=uwnd_levels, linewidths=4, colors='black', transform=ccrs.PlateCarree(),transform_first=True)

#### Colorbar and contour labels #####
cb = fig.colorbar(eof_fcontours, orientation='vertical', pad=0.03, extendrect=True, aspect=25, shrink=0.5)
cb.ax.tick_params(labelsize=16)
cb.set_label('(m s$^{-1}$) (std$^{-1}$)', size=18)
plt.clabel(lon_contours, fmt='%d', fontsize=12)
plt.clabel(lat_contours, fmt='%d', fontsize=12)
plt.clabel(uwnd_contours, fmt='%d', fontsize=12)

##### Plot two titles, one on right and left side ######
plt.title('ERA5 EOF1 of '+plev+'-hPa Zonal Wind Anomalies (Sept-May 1979-2014)', loc='left', fontsize=20)

##### Save figure #####
eof1filename = 'ERA5_EOF1_'+plev+'hpa_'+datafreq+'.pdf'
fig_path = os.path.join(output_data_path, eof1filename)
fig.savefig(fig_path)    # change file name here #

######################### Figure 2: Create plot of ERA5 EOF2 patterns #######################
mapcrs = ccrs.PlateCarree(central_longitude=180)

# Start the figure and create plot axes with proper projection
fig = plt.figure(2, figsize=(20, 14))
ax = plt.subplot(111, projection=mapcrs)
ax.set_extent([100, 240, 10, 80], ccrs.PlateCarree())   

# Add geopolitical boundaries for map reference
ax.add_feature(cfeature.LAND, facecolor="#bdbdbd")
countries = NaturalEarthFeature(category="cultural", scale="110m", facecolor="none", name="admin_0_boundary_lines_land")
ax.add_feature(countries, linewidth=0.5, edgecolor="black")
ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.5)
ax.coastlines('50m', linewidth=0.8)

# Set up contour and fill intervals
eof_levels = [-16,-14,-12,-10,-8,-6,-4,-2,2,4,6,8,10,12,14,16]
uwnd_levels = np.arange(30,65,5)
lat_levels = np.arange(20,80,20)
lon_levels = np.arange(100,240,20)

# Plot the variables
eof_fcontours = plt.contourf(lons_eof, lats_eof, eof2, levels=eof_levels, cmap=get_cmap('RdBu_r'), alpha=1, transform=ccrs.PlateCarree(),transform_first=True)
lon_contours = plt.contour(lons_eof, lats_eof, lons_eof, levels=lon_levels, colors="grey", linewidths=1, linestyles='dashed', transform=ccrs.PlateCarree())
lat_contours = plt.contour(lons_eof, lats_eof, lats_eof, levels=lat_levels, colors="grey", linewidths=1, linestyles='dashed', transform=ccrs.PlateCarree())
uwnd_contours = plt.contour(lons_eof, lats_eof, season_mean, levels=uwnd_levels, linewidths=4, colors='black', transform=ccrs.PlateCarree(),transform_first=True)

#### Colorbar and contour labels #####
cb = fig.colorbar(eof_fcontours, orientation='vertical', pad=0.03, extendrect=True, aspect=25, shrink=0.5)
cb.ax.tick_params(labelsize=16)
cb.set_label('(m s$^{-1}$) (std$^{-1}$)', size=18)
plt.clabel(lon_contours, fmt='%d', fontsize=12)
plt.clabel(lat_contours, fmt='%d', fontsize=12)
plt.clabel(uwnd_contours, fmt='%d', fontsize=12)

##### Plot two titles, one on right and left side ######
plt.title('ERA5 EOF2 of '+plev+'-hPa Zonal Wind Anomalies (Sept-May 1979-2014)', loc='left', fontsize=20)

##### Save figure #####
eof2filename = 'ERA5_EOF2_'+plev+'hpa_'+datafreq+'.pdf'
fig_path = os.path.join(output_data_path, eof2filename)
fig.savefig(fig_path)    # change file name here #

################ Figure 3 - Creates scatterplot of pcs in the NPJ phase diagram  ######################
plt.figure(3)

for i in range(len(pcs)):   
	s1 = plt.plot(pcs[:,0],pcs[:,1],'ko',markersize=8,markerfacecolor='g',markeredgewidth=1,markeredgecolor='k')

xaxe = plt.plot([-4,4],[-4,4],'k',linewidth=3) 
yaxe = plt.plot([-4,4],[4,-4],'k',linewidth=3) 

axes = plt.axis([-4, 4, -4, 4])
xlab = plt.xlabel('PC 1',fontsize=12,fontweight='bold')
ylab = plt.ylabel('PC 2',fontsize=12,fontweight='bold') 
plt.text(-3.75,0,'Jet Retraction',fontsize=14,fontweight='bold',color='r',horizontalalignment='center',verticalalignment='center',rotation=90)
plt.text(3.75,0,'Jet Extension',fontsize=14,fontweight='bold',color='r',horizontalalignment='center',verticalalignment='center',rotation=90)
plt.text(0,-3.75,'Equatorward Shift',fontsize=14,fontweight='bold',color='r',horizontalalignment='center',verticalalignment='center',rotation=0)
plt.text(0,3.75,'Poleward Shift',fontsize=14,fontweight='bold',color='r',horizontalalignment='center',verticalalignment='center',rotation=0)
titl = plt.title('NPJ Phase Diagram',fontsize=14,fontweight='bold')
plt.grid(True)
npjpdfilename = 'NPJphasediagram_scatterplot_'+plev+'hpa_'+datafreq+'.pdf'
fig_path = os.path.join(output_data_path, npjpdfilename)
plt.savefig(fig_path)    # change file name here #

################ Figure 4 - Creates bar plot that describes frequency of NPJ regimes in dataset  #################
ig4 = plt.figure(4, figsize=(14, 12))
ax4 = plt.subplot(111)

regfreq = (npjreg/len(pcs))*100
maxfreq = np.max(regfreq)

for spine in ax4.spines.values():
    spine.set_linewidth(4)

regimes = ['Jet'+"\n"+'Extension','Jet'+"\n"+'Retraction','Poleward'+"\n"+'Shift','Equatorward'+"\n"+'Shift','Origin']
npjreg_percent = (npjreg/len(pcs))*100
hist_tot = plt.bar(regimes,(npjreg/len(pcs))*100,color=['gold','mediumseagreen','dodgerblue','orangered','darkorchid'], edgecolor='black', linewidth=4)

ax4.set_ylim([0,maxfreq+5])
plt.yticks(np.arange(5,maxfreq+5,5), fontsize=18)
plt.grid(axis='y')
plt.tick_params(axis='x', labelsize=18)

plt.xlabel("North Pacific Jet Regime",fontsize=24,labelpad=20)
plt.ylabel("Frequency (Percent of Days)",fontsize=24,labelpad=20)

##### Plot two titles, one on right and left side ######
plt.title('NPJ Regime Frequency', loc='left', fontsize=24)

##### Save figure #####
npjfreqfilename = 'npj_regime_frequencies_'+plev+'hpa_'+datafreq+'.pdf'
fig_path = os.path.join(output_data_path, npjfreqfilename)
ig4.savefig(fig_path)    # change file name here #

#####################################################################################
################## Write Output Metadata ############################################
#####################################################################################

logging.info("Writing Metadata File")
current_date = datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S")+" UTC"
meta_json = {}
meta_json["provenance"] = {
    "environment": get_package_versions(),
    "data type": model,
    "data frequency": datafreq,
    "pressure level": plev,
    "modeldata": data_path,
    "log": "regimes.log",
    "date": current_date}
meta_json["plots"] = {
    "EOF 1 pdf": {
        "filename": eof1filename,
        "long_name": "EOF 1 of ERA5 Zonal Wind Anomalies over the North Pacific (1979-2014)",
        "description": "EOF 1 of ERA5 Zonal Wind Anomalies"},
    "EOF 2 pdf": {
        "filename": eof2filename,
        "long_name": "EOF 2 of ERA5 Zonal Wind Anomalies over the North Pacific (1979-2014)",
        "description": "EOF 2 of ERA5 Zonal Wind Anomalies"},
    "NPJ phase diagram scatterplot pdf": {
        "filename": npjpdfilename,
        "long_name": "Scatterplot of NPJ projections onto the NPJ phase diagram",
        "description": "NPJ projections onto the NPJ phase diagram"},
    "NPJ regime frequency pdf": {
        "filename": npjfreqfilename,
        "long_name": "Percent Frequency of NPJ regimes",
        "description": "Percent Frequency of NPJ regimes"}}
meta_json["data"] = {
    "NPJ principal components": {
        "filename": pcfilename,
        "long_name": "Timeseries of NPJ principal components 1 and 2, and the classified NPJ regime",
        "description": "Principal Components 1 and 2 and the NPJ regime"}}

output_file_name = os.path.join(output_data_path, "output.json")
write_json(meta_json, output_file_name)
