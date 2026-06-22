# NPJ Phase

Updated: 22 June 2026

This is a CMEC-compliant module that evaluates the daily and monthly variability of the North Pacific jet stream during the cool season within gridded model datasets.

## Introduction

The variability of the North Pacific jet stream during the cool season (September–May) is defined by applying EOF analysis to identify the two leading modes of variability of upper-tropospheric (200, 250, or 300-hPa) zonal wind anomalies over the North Pacific (100-240E; 10-80N) during the cool season on daily or monthly timescales. The first EOF corresponds to a zonal extension or retraction of the climatological North Pacific jet stream, whereas the second EOF corresponds to a poleward or equatorward shift of the climatological jet-exit region. These EOFs are qualitatively similar when defined on both daily and monthly timescales, and graphical depictions of these EOF patterns can be found in [Winters et al. 2019a, their Fig. 1](https://doi.org/10.1175/WAF-D-18-0106.1).

The utility of this approach is that instantaneous daily or monthly zonal wind anomalies can be projected onto these EOF patterns, producing a couplet of principal components that can be plotted on a two-dimensional phase diagram [Winters et al. 2019a, their Fig. 4](https://doi.org/10.1175/WAF-D-18-0106.1). Using this North Pacific jet phase diagram, we are able to define a set of 5 North Pacific jet regimes that characterize the prevailing flow pattern across the North Pacific. Each regime is associated with distinct impacts on temperatures and precipitation downstream over North America ([Winters et al. 2019a, their Fig. 5](https://doi.org/10.1175/WAF-D-18-0106.1), [Winters et al. 2019b](https://doi.org/10.1175/WAF-D-18-0168.1), [Winters and Walker 2022](https://doi.org/10.1175/JAMC-D-21-0211.1), [Winters and Attard 2022](https://doi.org/10.1175/WAF-D-21-0203.1), and each regime is associated with different degrees of predictive skill on medium-range to subseasonal timescales ([Winters et al. 2019a](https://doi.org/10.1175/WAF-D-18-0106.1), [Winters 2021](https://doi.org/10.1029/2021JD035094), [Henderson and Winters 2026](https://doi.org/10.1175/WAF-D-25-0170.1)). 

This module permits the classification of these different NPJ regimes within any gridded model dataset that is provided as input. Input data is evaluated against daily or monthly EOF patterns that are defined based on ERA5 zonal wind anomalies during September 1979-2014. Anomalies on a daily timescale are calculated relative to a daily ERA5 climatology computed by using a 21-day moving window centered on each day across all years between 1979-2014. Monthly anomalies are defined based on the calendar month using ERA5 data between 1979-2014. ERA5 climatology files are provided as part of the module and are included in the "climo_files" folder. Files with EOF patterns describing the daily or monthly variability of the North Pacific jet stream are also included within the "climo_files" folder. These files, and the zonal wind climatologies, are required for the module to work.

## Input Data Requirements

The module is designed to work with any gridded dataset that has been pre-processed appropriately. In particular, any input dataset must be in netcdf format and restricted to a single calendar year (i.e., 365 timesteps for daily data or 12 timesteps for monthly data). Full zonal wind data at 200, 250, or 300 hPa should be used (do not calculate anomalies as these calculations are performed by the module). 

Input data must be regridded into a 1x1 degree lat/lon format (180x360) extending between 0.5-379.5 degrees East and -89.5 to 89.5 degrees North. Smaller horizontal domains are permitted, so long as the input horizontal grid spacing is 1x1 degree and data are continuous between 10.5-79.5 degrees North and 100.5-239.5 degrees East. The coordinate names for the input dataset should be [time, level, lat, lon], where time is a datetime object, level is the pressure in hPa, and the zonal wind variable is defined as "u". More information on how to read in your input dataset is provided in the "user settings" section below.

Two exceptions to the above criteria are allowed to streamline input data requirements for the module. In particular, direct support is provided for [ERA5 daily-averaged](https://cds.climate.copernicus.eu/datasets/derived-era5-pressure-levels-daily-statistics?tab=download) and [ERA5 monthly-averaged](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels-monthly-means?tab=overview) datasets downloaded from the Copernicus Data Store. As above, input data to the module should be restricted to a single calendar year, but no regridding or reformatting is required, and the module should work with these ERA5 files "as is". The module is also built to work directly with regridded data from E3SMv3. The use of E3SMv3 and ERA5 data as input to the module is specified by a custom user setting before running the module.

### Tips for Regridding Input Data

As mentioned above, it is required for input datasets to be regridded and reformatted prior to running the module. To help facilitate regridding spatial data to the correct format, a regridding file is provided in the "input_files" folder ("NPJregrid.txt") for use with the Climate Data Operators (CDO) package. A sample command to regrid lat/lon data to the required input format is as follows:

`cdo -remapbil,NPJregrid.txt -sellevel,<INSERT_PRESSURE_LEVEL> -select,name=<INSERT_ZONAL_WIND_VARIABLE_NAME> <INPUT_FILE> <OUTPUT_FILE>`

The names of variables and coordinates can also be renamed using CDO in order to format the input data correctly. A sample command for renaming variables or coordinates is as follows:

`cdo -chname,<OLD_NAME>,<NEW_NAME> <INPUT_FILE> <OUTPUT_FILE>`

For E3SM data, target remapping files are also provided in the "input_files" folder to regrid both low-resolution (LR) and NARRM E3SMv3 data to the required lat/lon grid. For this purpose, the ncremap package can be particularly useful, and a sample command for regridding E3SMv3 LR data is as follows:

`ncremap -m map_ne30pg2_to_cmip6_180x360_aave.20200201.nc <INPUT_FILE> <OUTPUT_FILE>`

## Installation

First, please use git clone to obtain a local copy of this repository.

The module is run via the cmec-driver command line program ([code repository](https://github.com/cmecmetrics/cmec-driver)), which has its own [installation instructions](https://github.com/cmecmetrics/cmec-driver#installation). Be sure that the cmec-driver program and its environmental variables are set-up to recognize your local source file for conda and python environments.

### Python Environment    
This module depends on a few different python packages along with other modules from the Python standard library. An environment called "_CMEC_npjphase_env", which includes these packages, must be created before running the module for the first time.

A yaml file is provided with the source code for this module to create this environment. The environment can be created by running the following code locally: 

`conda env create -f npjphase_env.yaml`

### Register The Module 
Activate an existing python environment with cmec-driver installed. You can then register this module by using the following command:

`cmec-driver register path/to/NPJphase/`  

This command will update your cmec.json file in your ~/.cmec folder with a list of default user parameters that can be changed.

### Custom User Settings

Once you have registered the module, you can update the user settings in cmec.json to work with your input dataset. The following settings are allowable:

pressure_level: "200", "250", or "300"

frequency: "daily" or "month"

data_type: "era5", "e3sm", or "other"

input_dataset: <INSERT_INPUT_FILE_NAME>

A default input dataset with monthly resolution is provided from ERA5 in the "input_files" folder as part of the module for testing purposes. This dataset will work with the default settings that are loaded into cmec.json when the module is registered.

## Running The Module
Activate a python environment with cmec-driver installed. If an output directory does not already exist, create one. Use the "model_directory" that contains the input dataset that you'd like to evaluate.

`cmec-driver run model_directory/ output_directory/ NPJphase`  

Navigate into the "output_directory" folder to view the results. The module will produce 4 different plots. Two of the plots show the climatological zonal wind during the cool season from ERA5 and the corresponding EOF patterns for the configuration you've chosen. The other two plots show the percent frequency of each NPJ regime within your input dataset, as well as a scatterplot of where the NPJ projected onto the NPJ phase diagram for each timestep within the input dataset. A text file is also produced with the principal component couplet for each timestep and the corresponding NPJ regime classification. 

## Acknowledgement
Content in this repository was developed through support provided by the U.S. Department of Energy, Office of Science, Office of Biological and Environmental
Research under Award Number DE-SC-0024002.

## License

MIT License

Copyright (c) 2026 Andrew Winters

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


