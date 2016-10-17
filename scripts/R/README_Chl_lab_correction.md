# Overview of correcting Chl from gain profiles and lab values

## Flowchart

![r1 flowchart](R_processing_flowchart.svg)

## Overview

The water quality chlorophyll measurements collected during the transects get corrected in post-processing using the vertical gain profiles and the lab values. The vertical profiles are collected several times during a sampling day using different gain settings. Depths below the top 1m of the water column are discarded - the values for the top 1m are averaged for each of the profiles. These daily average value for the site profile is compared to a grab sample that is processed back in the lab for chlorophyll content using a linear regression. This linear regression equation is then applied to the water quality transect data. 
