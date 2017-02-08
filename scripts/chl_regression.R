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
  lowerbound = paste(date, '00:00:00.000000')
  upperbound = paste(date, '23:59:59.999999')
  con = dbConnect(SQLite(), dbname=database) # connect to the sqlite database

  # build query statement  
  statement = paste("select * from vertical_profiles where date_time >'", lowerbound, "'", "and date_time <'", upperbound, "'", sep='')
  print(statement)
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
  print(statement)
  grab = dbGetQuery(con, statement) 
  dbDisconnect(con) # disconnect from the database
  return(grab) # returns all vertical profile records for a given date
}


# date to pass to database
readdate <- function()
{ 
  n <- readline(prompt="Enter an date: ")
  return(as.Date(n))
}


############################################################
date = '2013-01-07'

#as.Date(date)
p <- vertical_profiles(date)






