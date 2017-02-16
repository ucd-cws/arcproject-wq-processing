############################################################
# install the packages to library

if(!require(RSQLite)){
  install.packages("RSQLite")
  library(RSQLite)
}

if(!require(plyr)){
  install.packages("plyr")
  library(plyr)
}

if(!require(ggplot2)){
  install.packages("ggplot2")
  library(ggplot2)
}


#############################################################
# helper functions

# queries database to get all the vertical profile water data for a given day ie '2013-01-07'
vertical_profiles <- function(date, gain){
  lowerbound = paste(date, '00:00:00.000000')
  upperbound = paste(date, '23:59:59.999999')
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database
  statement = sprintf("select * from vertical_profiles, profile_sites where date_time > '%s' and date_time < '%s' and profile_sites.id=vertical_profiles.profile_site_id AND vertical_profiles.gain_setting = '%s'", lowerbound, upperbound, gain)
  vps = dbGetQuery(con, statement)
  dbDisconnect(con) # disconnect from the database
  return(vps) # returns all vertical profile records for a given date
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

grab_dates <- function(){
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database
  statement = "SELECT DISTINCT date(date) AS dates FROM grab_samples"
  datesdf = dbGetQuery(con, statement)
  uniq_dates <- as.vector(datesdf$dates)
  dbDisconnect(con) # disconnect from the database
  return(uniq_dates) # returns a vector (list) of unique dates with vertical profile records
}


# check that date has wqp and grab samples
check_date <- function(date){
  possible_wqp_dates <- wqp_dates()
  possible_grab_dates <- grab_dates()
  if(date %in% possible_wqp_dates == FALSE){
    stop(paste("Data for", date, "does not exist in the vertical_profiles table."))
  }
  else if(date %in% possible_grab_dates == FALSE){
    stop(paste("Data for", date, "does not exist in the grab_sample table."))
  }
  else{
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
  means <-ddply(wqp, .(profile_site_id, abbreviation), summarize, chl_profile=mean(chl))
  return(means)
}

# grab the profile data from the database, process it to return avg wq per site
profile <- function(date, gain){
  check_date(date)
  wqp_for_date <-vertical_profiles(date, gain)
  wqp_top_m <- wqp_1m(wqp_for_date)
  profile_avgs <- wqp_avg_by_site(wqp_top_m)
  return(profile_avgs)
}


# query to get grab samples
grab<- function(date){
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database
  statement = sprintf("select grab_samples.profile_site_id as profile_site_id, profile_sites.abbreviation as abbreviation, chlorophyll_a as chl_grab 
                      from grab_samples, profile_sites where date == '%s' AND grab_samples.profile_site_id == profile_sites.id", date)
  vps = dbGetQuery(con, statement)
  dbDisconnect(con) # disconnect from the database
  return(vps) # returns all vertical profile records for a given date
}


# check that both the profiles and the grabs have the same site codes
check_site_names <- function(profiles, grabs){
  p_names <- sort(as.vector(profiles$abbreviation))
  g_names <- sort(as.vector(grabs$abbreviation))
  if(all.equal(p_names, g_names)==TRUE){
    return(TRUE)
  }
  else{
    a <- paste(p_names, collapse=" ")
    b <- paste(g_names, collapse=" ")
    st = sprintf("Site codes do not match. \n Rename either the profiles or the grab samples! \n vertical_profile codes [%s] \n grab_sample codes [%s].", a, b)
    #warning(st)
    stop(st)
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


# lookup profile_site id by abbreviation
lookup_profile_site_id<-function(code){
  code = toupper(code)
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database
  statement <- sprintf("SELECT id from profile_sites where abbreviation == '%s'", code)
  res <- dbGetQuery(con, statement)
  id <- res[[1,1]]
  return(id)
}



plot_regression <- function(merged_data, title){
 plot.title = title
 t <- lm_results(merged_data)
 
 eq <- substitute(italic(y) == a + b %.% italic(x)*","~~italic(r)^2~"="~r2, 
                  list(a = format(t[1], digits = 2), 
                       b = format(t[2], digits = 2), 
                       r2 = format(t[3], digits = 3)))
 
 plot.subtitle = eq
 
 p <- ggplot(merged_data, aes(x=chl_profile, y=chl_grab, label=abbreviation)) +
    geom_smooth(method=lm,   # Add linear regression line
                se=FALSE) +    # Don't add shaded confidence region
   geom_point(size=2.5) +    # Use hollow circles
   theme_bw() +
   ylab("CHL Lab")+ 
   xlab("CHL Field")+
   geom_text(nudge_x = 0.33) +
   ggtitle(bquote(atop(.(plot.title), atop(italic(.(plot.subtitle)), "")))) 
  return(p)  
}


lm_results <- function(merged_data){
  l <- lm(merged_data$chl_grab~merged_data$chl_profile)
  model_summary <- summary(l)
  a <- model_summary$coefficients[1,1]
  b <- model_summary$coefficients[2,1]
  r <- model_summary$r.squared
  print(a, b, r)
  coffs_r <- c(a, b, r)
  return(coffs_r)
}


add_regression_to_db<-function(date, gain, a_coeff, b_coeff, rsquared){
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database
  statement = sprintf("INSERT INTO regression(date, gain, r_squared, a_coefficient, b_coefficient)
  VALUES('%s', '%s', '%s', '%s', '%s')", date, gain, rsquared, a_coeff, b_coeff)
  dbSendQuery(con, statement)
  print("added regression info to data base")
}


confirm_commit <- function(func){
  ans <- readline("Commit regression to the database? press y for yes   ")
  if(ans=='y'){
    func
  }
  else{
    print("Not commiting regression")
  }
}

