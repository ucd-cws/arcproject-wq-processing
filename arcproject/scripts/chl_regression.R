#############################################################

# project settings

# set working directory to arcproject-wq-processing folder
# get the base folders
project_folder = Sys.getenv("arcproject_code_path")  # get the main folder name
database = Sys.getenv("arcproject_db_path")  # get the DB location

setwd(project_folder)

library("RSQLite")
library(plyr)

#############################################################
# helper functions

# queries database to get all the vertical profile water data for a given day ie '2013-01-07'
vertical_profiles <- function(date){
  lowerbound = paste(date, '00:00:00.000000')
  upperbound = paste(date, '23:59:59.999999')
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database
  # build query statement
  #statement = paste("select * from vertical_profiles where date_time >'", lowerbound, "'", "and date_time <'", upperbound, "'", sep='')
  statement = sprintf("select * from vertical_profiles where date_time > '%s' and date_time < '%s'", lowerbound, upperbound)
  vps = dbGetQuery(con, statement)
  dbDisconnect(con) # disconnect from the database
  return(vps) # returns all vertical profile records for a given date
}

# queries database to get all grab sample data for a given day ie '2013-01-07'
vertical_profiles <- function(date){
  lowerbound = paste(date, '00:00:00.000000')
  upperbound = paste(date, '23:59:59.999999')
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database
  #statement = paste("select * from vertical_profiles where date_time >'", lowerbound, "'", "and date_time <'", upperbound, "'", sep='')
  statement = sprintf("select * from vertical_profiles where date_time > '%s' and date_time < '%s'", lowerbound, upperbound)
  grab = dbGetQuery(con, statement)
  dbDisconnect(con) # disconnect from the database
  return(grab) # returns all vertical profile records for a given date
}

# date to pass to database
readdate <- function()
{
  n <- readline(prompt="Enter an date: ")
  return(n)
}

# unique wq dates
wqp_dates <- function(){
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database
  statement = "SELECT DISTINCT date(date_time) AS dates FROM vertical_profiles"
  datesdf = dbGetQuery(con, statement)
  uniq_dates <- as.vector(datesdf$dates)
  dbDisconnect(con) # disconnect from the database
  return(uniq_dates) # returns a vector (list) of unique dates with vertical profile records
}

# check that date has wqp and grab samples
check_date <- function(date){
  possible_wqp_dates <- wqp_dates()
  if(date %in% possible_wqp_dates == FALSE){
    stop(paste("Data for", date, "does not exist in the vertical_profiles table."))
  }else{
    print("Checked date")
  }
}

# subset all profiles to just the top 1m of the depth field
wqp_1m<-function(wqp_for_a_day){
  topm <- subset(wqp_for_a_day, dep_25 > 0 & dep_25<1)
  return(topm)
}

# average water quality profile grouping by site id
wqp_avg_by_site<-function(wqp){
  means <-ddply(wqp, .(profile_site_abbreviation), summarize, temp=mean(temp), ph=mean(ph), sp_cond=mean(sp_cond),
        salinity=mean(salinity), dissolved_oxygen=mean(dissolved_oxygen), dissolved_oxygen_percent=mean(dissolved_oxygen_percent),
        dep_25=mean(dep_25),par=mean(par), rpar=mean(rpar), turbidity_sc=mean(turbidity_sc), chl=mean(chl))
  return(means)
}

# grab the profile data from the database, process it to return avg wq per site
profile <- function(date){
  check_date(date)
  wqp_for_date <-vertical_profiles(date)
  wqp_top_m <- wqp_1m(wqp_for_date)
  profile_avgs <- wqp_avg_by_site(wqp_top_m)
  return(profile_avgs)
}


# query to get grab samples

# TODO TODO TODO
grab_df<- function(){
  library(readr)
  df <- read_csv(paste(project_folder, "arcproject/data/legacy/wq_grab/ArcProject_lab_values_Master.csv", sep="/"))
  df$date <- as.Date(df$date, "%m/%d/%Y")
  return(df)
}

# subset grab by date - TODO this will be part of the query????
grab_single_day<-function(df, desired_date){
  s <- subset(df, date == desired_date)
  return(s)
}

# check that both the profiles and the grabs have the same site codes
check_site_names <- function(profiles, grabs){
  p_names <- as.vector(profiles$profile_site_abbreviation)
  g_names <- as.vector(grabs$site_id)
  if(all.equal(p_names, g_names)==TRUE){
    return(TRUE)
  }
  else{
    a <- paste(p_names, collapse=" ")
    b <- paste(g_names, collapse=" ")
    st = sprintf("Site codes do not match. \n Rename either the profiles or the grab samples! \n vertical_profile codes [%s] \n grab_sample codes [%s].", a, b)
    warning(st)
    return(FALSE)
  }
}

# add new site to the profile table if it does not exist
new_profile_site <- function(new_site){
  # check if the new site is in the profile site table
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database
  statement = sprintf("SELECT COUNT(*) as num FROM profile_sites WHERE abbreviation == '%s'", new_site)
  count = dbGetQuery(con, statement)
  if(count$num == 0){
    # add new site
    statement = sprintf("INSERT into profile_sites (abbreviation) VALUES('%s')", new_site)
    dbGetQuery(con, statement)
  }
  else{
    print("Site already exists")
  }
  dbDisconnect(con) # disconnect from the database
}

# update vertical profile record with new site name
update_wqp_site <- function(date, current_site, new_site){
  # add new site to profile table if needed
  new_profile_site(new_site)
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database
  # build query statement
  lowerbound = paste(date, '00:00:00.000000')
  upperbound = paste(date, '23:59:59.999999')
  statement <- sprintf("UPDATE vertical_profiles SET profile_site_abbreviation='%s' where date_time > '%s' and date_time < '%s' and profile_site_abbreviation='%s'", new_site, lowerbound, upperbound, current_site)
  print(statement)
  dbGetQuery(con, statement)
  dbDisconnect(con) # disconnect from the database
}


############################################################
adate = '2013-01-07'

p <- profile(adate)
g <- grab_single_day(grab_df(), adate)

check_site_names(p, g)

