# WQ_postprecessing.R
# Attempt to replicate the Arc Project's legacy code to
# correct chlorophyll values.

############################################################

# Original script - 1_WQp_Processing.R
# Corrects the wq data using lab-derived chlorophyll values


# lines 27-35

# load in the monthly water quality transect data (from csv)
# then filter out bad values (salinity>0, CHL < CHL < 2.000e+06, TurbSC < 3000)
# subset data by sampling day

subset_monthly_wqt_by_day <- function(monthly_wqt_csv, subset_date){
	# imports monthly water quality transect from csv to r data frame, removes bad values, and splits into sperate df by date
	# example date "9/15/2014"
  water_quality_file <- read.csv(monthly_wqt_csv, header=TRUE, stringsAsFactors=FALSE)

	# removes rows bad values
	water_quality_wo_bad_values <- rm_bad_values(water_quality_file)

	# not sure why they split by date. Alternative could be split, apply, combine 
	wqt_by_date <- subset(water_quality_wo_bad_values,water_quality_wo_bad_values$Date==subset_date)
	#wqt_by_date <- split(water_quality_wo_bad_values, water_quality_wo_bad_values$Date, drop=TRUE)
	return(wqt_by_date)
	
  }


rm_bad_values <- function(df){
  # removes "bad" values from a dataframe and returns a "clean" data frame with those rows removed
  
  # TODO - check if the file contains these columns (Sal, CHL, TurbSC)
  df_wo_bad_rows <- df[which(df$Sal > 0 & df$CHL < 2.000e+06 & df$TurbSC<3000),]
  
  return (df_wo_bad_rows)
}



# lines 39 - 59

# opens the daily profile files for GN10 and GN1, creates Date_Site columns,
# filters out bad data (sub 1m) and aggregates by sites, joins 1m means with the lab values based function
# the siteID, then saves the table.

load_gain_file <- function(gain_file ){
  #loads the daily gain csv file, adds siteID (site + date), removes bad data, 
  gain <- read.csv(gain_file, header=TRUE, stringsAsFactors=FALSE)
  
  # adds SiteID column by combining site and date 
  gain$SiteID <- paste(gain$Site,gain$Date,sep="_")
  
  # removes "bad" rows using the rm_bad_values function
  gain_valid <- rm_bad_values(gain)
  
  # removes rows that are deeper than 1m using the rm_rows_deeper_than_1m function and depth field
  gain_1m <- rm_rows_deeper_than_1m(gain_valid)
  
  return(gain_1m)
  
}


rm_rows_deeper_than_1m <- function(data_for_all_depths){
  # removes rows that have values in the depth field greater than 1m meter
  
  # subset dateframe using citeria
  data_1m_below_surface_only <- data_for_all_depths[which(data_for_all_depths$DEP25 < 1),]        
  
  return(data_1m_below_surface_only)
  }


mean_gain_by_sitedate <- function(gain1m){
  # summarizes gain by mean values for site-date (use 1m surface gain file as input)
  mean_sitedate <- aggregate(gain1m, by=list(gain1m$SiteID), FUN=mean, na.rm=FALSE, stringsAsFactors=False)
  
  # renames columns
  colnames(mean_sitedate)[colnames(mean_sitedate) == "SiteID"] <- "NA"
  colnames(mean_sitedate)[colnames(mean_sitedate) == "Group.1"] <- "SiteID"
  
  return(mean_sitedate)
}


load_chl_labvalues <- function(chl_lab_values_csv){
  # loads csv with the lab sample results
  chl_lab <- read.csv(chl_lab_values_csv,stringsAsFactors=FALSE)
  return(chl_lab)
}

join_sitemeans_w_labvalues <- function(chl_lab, gain1m_sitemeans){
  #Joins 1m means with the lab values based on SiteID.
  joined <- merge(gain1m_sitemeans, chl_lab, by="SiteID")
  #Renames column.
  colnames(joined)[colnames(joined) == "Chlorophyll.a"] <- "CHL2"
  return(joined)
}

save_joined_lab_gain <- function(joined_lab_gain_file, output_location){
  write.table(joined_lab_gain_file, output_location) 
}


# lines 61-75
# linear model and graph regression equation

chl_lab_regression <- function(joined_chl_df){
  
  # linear model for chl values
  chl_lm <- lm(joined_chl_df$CHL2~joined_chl_df$CHL) # CHL2 = lab, CHL=vert gain profile
  
  return(chl_lm)
}

daily_scatter_graph <- function(joined_chl_df, lm_out, output_graph, title){
  jpeg(file=output_graph)
  
  # output from linear model
  # coefficients of linear model 
  chl_lm_coeff <- coefficients(lm_out)
  a <- signif(chl_lm_coeff[1], digits = 3)
  b <- signif(chl_lm_coeff[2], digits = 3)
  summary <- summary(lm_out, digits=3)
  r2 <- summary$r.squared
  
  
  # equation for graph? 
  eq <- paste("R^2", " = ", r2," , y = ",b,"x + ",a, sep="")
  
  
  plot(joined_chl_df$CHL,joined_chl_df$CHL2,main=title, ylab="Lab_chl",xlab="Field_chl", sub=eq)
  abline(lm_out)
  dev.off()
}

save_lm_to_csv <- function(){
  # TODO save out lm results to csv file
}

# lines 77-83

#apply regression equation to transect data for that date
#wq_gn1$NewCHL <- paste(NewCHL=coeffs_gn1[1] + coeffs_gn1[2]*wq_gn1$CHL)

apply_regression <- function(wq_transect, lm, column_name){
  coeff <- coefficients(lm)
  coeff_a <- unname(coeff[1])
  coeff_b <- unname(coeff[2])
  wq_transect[column_name]<- coeff_a + coeff_b*wq_transect$CHL
  return(wq_transect)
} 
