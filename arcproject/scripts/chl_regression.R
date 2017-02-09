#############################################################
# project settings

# set working directory to arcproject-wq-processing folder
project_folder = "~/arcproject-wq-processing"
setwd(project_folder)

# location of database
database = 'wqdb.sqlite'


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
  statement = paste("select * from vertical_profiles where date_time >'", lowerbound, "'", "and date_time <'", upperbound, "'", sep='')
  vps = dbGetQuery(con, statement) 
  dbDisconnect(con) # disconnect from the database
  return(vps) # returns all vertical profile records for a given date
}

# queries database to get all grab sample data for a given day ie '2013-01-07'
vertical_profiles <- function(date){
  lowerbound = paste(date, '00:00:00.000000')
  upperbound = paste(date, '23:59:59.999999')
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database
  # build query statement  
  statement = paste("select * from vertical_profiles where date_time >'", lowerbound, "'", "and date_time <'", upperbound, "'", sep='')
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
  # build query statement  
  statement = paste("SELECT DISTINCT date(date_time) AS dates FROM vertical_profiles")
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

############################################################
date = '2013-01-07'

profile(date)
