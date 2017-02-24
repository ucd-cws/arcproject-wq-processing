# template for working with chl regression

# user parameters
date <- '2013-01-07'
gain_setting <- 0

#########################################################

# project settings
# set working directory to arcproject-wq-processing folder
project_folder = "~/arcproject-wq-processing"
setwd(project_folder)

# location of database
database = 'arcproject/wqdb.sqlite'

# source the chl_regression equations
source('arcproject/scripts/chl_regression.R')


#########################################################
# use functions defined in chl_regression.R to pull and process data

# get  all the data for a given data and gain setting from the profiles table
wqp_for_date <-vertical_profiles(date, gain_setting)

# subset dataframe by the top meter of the profile
wqp_top_m <- wqp_1m(wqp_for_date)

# average by the profile site
profile <- wqp_avg_by_site(wqp_top_m)

# now query the database to get the grab samples for the date
grab_samples <- grab(date)

############################################################
# check if all data has matches before merging
if(check_site_names(profile, grab_samples)){

# merge data 
field_lab_merged <- merge(profile, grab_samples, by="abbreviation")

# view data
View(field_lab_merged)

# plot regression
title <- paste(date, " - gain ", gain_setting, sep=" ")
p <-plot_regression(field_lab_merged, title)
p # view plot

# get the results from the lm 
lm_coeff <- lm_results(field_lab_merged)


# save plot
out <- paste(project_folder, '/arcproject/plots/regressions/', paste('reg_', date, '_', gain_setting, '.png', sep=''), sep='')
ggsave(filename = out, plot = p, width = 8, height = 6)

# add regression to table and save regression to folder
confirm_commit(add_regression_to_db(date, gain_setting, lm_coeff[1], lm_coeff[2], lm_coeff[3]))
}
