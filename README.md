# NPJ Phase

This is a CMEC-compliant module that evaluates the daily and monthly variability of the North Pacific jet stream during the cool season within gridded model datasets.

## Introduction

The variability of the North Pacific jet stream during the cool season (September–May) is defined by using EOF analysis to define the two leading modes of variability of upper-tropospheric (200, 250, or 300-hPa) zonal wind anomalies over the North Pacific during the cool season on daily or monthly timescales. The first EOF corresponds to a zonal extension or retraction of the climatological North Pacific jet stream, whereas the second EOF corresponds to a poleward or equatorward shift of the climatological jet-exit region. These EOFs are qualitatively similar on both daily and monthly timescales, and graphical examples of these EOF patterns can be found in [Winters et al. 2019a, their Fig. 1](https://doi.org/10.1175/WAF-D-18-0106.1).

The utility of this approach is that instantaneous daily or monthly zonal wind anomalies can be projected onto these EOF patterns, producing a couplet of principal components that can be plotted on a two-dimensional phase space [Winters et al. 2019a, their Fig. 4](https://doi.org/10.1175/WAF-D-18-0106.1). Using this phase diagram, we are able to define a set of 5 North Pacific jet regimes that can be used to characterize the prevailing flow pattern across the North Pacific. Each of these regimes are associated with distinct impacts on temperatures and precipitation downstream over North America ([Winters et al. 2019a, their Fig. 5](https://doi.org/10.1175/WAF-D-18-0106.1), [Winters et al. 2019b](https://doi.org/10.1175/WAF-D-18-0168.1), [Winters and Walker 2022](https://doi.org/10.1175/JAMC-D-21-0211.1), [Winters and Attard 2022](https://doi.org/10.1175/WAF-D-21-0203.1) and each regime is associated with different degrees of predictive skill on medium-range to subseasonal timescales ([Winters et al. 2019a](https://doi.org/10.1175/WAF-D-18-0106.1), [Winters 2021](https://doi.org/10.1029/2021JD035094), [Henderson and Winters 2026](https://doi.org/10.1175/WAF-D-25-0170.1). 

This module subsequently permits the identification of these different NPJ regimes within any gridded model dataset that is provided as input. Input data is evaluated against daily or monthly EOF patterns that are defined based on zonal wind anomalies from ERA5 during September 1979-2014. Anomalies on a daily timescale are calculated based on a daily climatology computed by using a 21-day moving window centered on each day. Monthly anomalies are defined based on the calendar month.

## Input Data Requirements

The module is designed to work with any gridded dataset that has been pre-processed appropriately. In particular, any input dataset must be in netcdf format and restricted to a single calendar year (i.e., 365 timesteps for daily data or 12 timesteps for monthly data). Full zonal wind data from 200, 250, or 300 hPa can be used (do not calculate anomalies as these are done by the module). 

Input data must be regridded into a 1x1 degree lat/lon format (180x360) extending from 0.5-379.5 degrees East and -89.5 to 89.5 degrees North. Smaller horizontal domains are permitted, so long as the horizontal grid spacing is 1x1 degree and data are continuous between 10.5-79.5 degrees North and 100.5-239.5 degrees East. The coordinates of the input dataset should be [time, level, lat, lon], where time is a datetime object and level is the pressure in hPa, and the zonal wind variable should be defined as "u". More information on how to read in your input dataset are provided in the "user settings" section below.

Two exceptions are allowed to streamline input data requirements for the module. In particular, support is provided for [ERA5 daily-averaged](https://cds.climate.copernicus.eu/datasets/derived-era5-pressure-levels-daily-statistics?tab=download) and [ERA5 monthly-averaged](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels-monthly-means?tab=overview) datasets downloaded from the Copernicus data store. As above, input data to the module should be restricted to a single calendar year. The module is also built to work directly with regridded data from E3SM. The use of E3SM and ERA5 data as input to the module is specified as a user setting.

### Regridding Input Data

As mentioned above, it is generally required for input datasets to be regridded prior to running the module. To help facilitate regridding spatial data to the correct format, a regridding file is provided as part of the module "NPJregrid.txt" for use with the Climate Data Operators (CDO) package. A sample command to regrid lat/lon data to the required input format is as follows:


