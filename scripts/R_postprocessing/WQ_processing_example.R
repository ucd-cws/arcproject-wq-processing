# WQ_processing_example.R

# set working directory
setwd("~/arcproject-wq-processing/scripts/R")

# load custom functions from WQ_postprocessing.R
source("WQ_postprocessing.R")

# water quality transect file
wq_transect_file <- "test_data/Arc_Sep2014_WQt_Import.csv"

# subset by date of interest
transect_singleday <- subset_monthly_wqt_by_day(wq_transect_file, "9/15/2014")



# gain files
gain_100_file <- "test_data/Arc_091514_wqp_gn100_trunc.csv"
gain_10_file <- "test_data/Arc_091514_wqp_gn10_trunc.csv"


# lab values
lab_csv <- "test_data/Arc_Project_chl_values_July14_Dec14.csv"
lab_values <- load_chl_labvalues(lab_csv)


# gain 10
gain10 <- load_gain_file(gain_10_file)
gain10_sitemeans <- mean_gain_by_sitedate(gain10)
joined_gain10 <- join_sitemeans_w_labvalues(lab_values, gain10_sitemeans)
reg10 <- chl_lab_regression(joined_gain10)
daily_scatter_graph(joined_gain10, reg10, "test_gain10.jpg", "Gain 10")


# gain 100
gain100 <- load_gain_file(gain_100_file)
gain100_sitemeans <- mean_gain_by_sitedate(gain100)
joined_gain100 <- join_sitemeans_w_labvalues(lab_values, gain100_sitemeans)
reg100 <- chl_lab_regression(joined_gain100)
daily_scatter_graph(joined_gain100, reg100, "test_gain100.jpg", "Gain 100")


# apply regression
transect_w_corrected_chl <- apply_regression(transect_singleday, reg10, "Chl_Gain10")
transect_w_corrected_chl <- apply_regression(transect_w_corrected_chl, reg100, "Chl_Gain100")

