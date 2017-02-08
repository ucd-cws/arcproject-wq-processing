#############################################################
# project settings

# set working directory to arcproject-wq-processing folder
project_folder = "~/arcproject-wq-processing"
setwd(project_folder)

# location of database
database = 'wqdb.sqlite'


library("RSQLite")

#############################################################
# helper functions



# queries database to get all the vertical profile water data for a given day ie '2013-01-07'
vertical_profiles <- function(date){
  date <- as.Date(date)# date should be cast to date object using as.Date()
  upperbound <- date + 1 # upper bound is the next day
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database
  print(date)
  print(upperbound)
  # build query statement  
  statement = paste("select * from vertical_profiles where date_time >=", date) #, "and date_time <", upperbound)
  print(statement)
  vps = dbGetQuery(con, statement) 
  dbDisconnect(con) # disconnect from the database
  return(vps) # returns all vertical profile records for a given date
}


# date to pass to database
readdate <- function()
{ 
  n <- readline(prompt="Enter an date: ")
  return(as.Date(n))
}


############################################################
date = '2013-01-07'

p <- vertical_profiles(date)