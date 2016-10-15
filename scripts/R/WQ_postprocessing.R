# WQ_postprecessing.R
# Attempt to replicate the Arc Project's legacy code to
# correct chlorophyll values and generate heatplots.

############################################################

# Original script - 1_WQp_Processing.R
# Corrects the wq data using lab-derived chlorophyll values


# lines 27-35

# part 1 - load in the monthly water quality transect data (from csv)
# then filter out bad values (salinity>0, CHL < CHL < 2.000e+06, TurbSC < 3000)
# subset data by sampling day

subset_monthly_wqt_by_day <- function(monthly_wqt_csv, date){
	# imports monthly water quality transect from csv to r data frame, removes bad values, and splits into sperate df by date
	water_quality_file <- read.csv(monthly_wqt_csv, header=TRUE, stringsAsFactors=FALSE)

	# removes rows bad values
	water_quality_wo_bad_values <- water_quality_file[which(water_quality_file$Sal > 0 & water_quality_file$CHL < 2.000e+06 & water_quality_file$TurbSC<3000),]

	# not sure what they do here? manually enter in the dates???
	wqt_by_date <- subset(water_quality_wo_bad_values)
}


rm_bad_values <- function(df){
  # removes "bad" values from a dataframe and returns a "clean" data frame with those rows removed
  
  # TODO - check if the file contains these columns (Sal, CHL, TurbSC)
  df_wo_bad_rows <- df[which(df$Sal > 0 & df$CHL < 2.000e+06 & df$TurbSC<3000),]
  
  return (df_wo_bad_rows)
}


rm_rows_deeper_than_1m <- function(data_for_all_depths){
  # removes rows that have values in the depth field greater than 1m meter
  
  # subset dateframe using citeria
  
  return(data_1m_below_surface_only)
}



# lines 39 - 59

# part 2 - opens the daily profile files for GN10 and GN1, creates Date_Site columns,
# filters out bad data (sub 1m) and aggregates by sites, joins 1m means with the lab values based function
# the siteID, then saves the table.
