# NPJ Phase

This is a CMEC-compliant module that evaluates the daily and monthly variability of the North Pacific jet stream during the cool season within gridded model datasets.

## Introduction

The variability of the North Pacific jet stream during the cool season (September–May) is defined by using EOF analysis to define the two leading modes of variability of upper-tropospheric (200, 250, or 300-hPa) zonal wind anomalies over the North Pacific during the cool season on daily or monthly timescales. The first EOF corresponds to a zonal extension or retraction of the climatological North Pacific jet stream, whereas the second EOF corresponds to a poleward or equatorward shift of the climatological jet-exit region. These EOFs are qualitatively similar on both daily and monthly timescales, and graphical examples of these EOF patterns can be found in [Winters et al. 2019a, their Fig. 1](https://doi.org/10.1175/WAF-D-18-0106.1).

The utility of this approach is that instantaneous daily or monthly zonal wind anomalies can be projected onto these EOF patterns, producing a couplet of principal components that can be plotted on a two-dimensional phase space [Winters et al. 2019a, their Fig. 4](https://doi.org/10.1175/WAF-D-18-0106.1). Using this phase diagram, we are able to define a set of 5 North Pacific jet regimes that can be used to characterize the prevailing flow pattern across the North Pacific. Each of these regimes are associated with distinct impacts on temperatures and precipitation downstream over North America ([Winters et al. 2019a, their Fig. 5](https://doi.org/10.1175/WAF-D-18-0106.1), [Winters et al. 2019b](https://doi.org/10.1175/WAF-D-18-0168.1), [Winters and Walker 2022](https://doi.org/10.1175/JAMC-D-21-0211.1), [Winters and Attard 2022](https://doi.org/10.1175/WAF-D-21-0203.1) and each regime is associated with different degrees of predictive skill on medium-range to subseasonal timescales ([Winters et al. 2019a](https://doi.org/10.1175/WAF-D-18-0106.1), [Winters 2021](https://doi.org/10.1029/2021JD035094), [Henderson and Winters 2026](https://doi.org/10.1175/WAF-D-25-0170.1). 

This module subsequently permits the identification of these different NPJ regimes within any gridded model dataset that is provided as input. Input data is evaluated against daily or monthly EOF patterns that are defined based on zonal wind anomalies from ERA5 during September 1979-2014. Anomalies on a daily timescale are calculated based on a daily climatology computed by using a 21-day moving window centered on each day. Monthly anomalies are defined based on the calendar month.

## Input Data Requirements

The mod
