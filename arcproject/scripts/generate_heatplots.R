if(!require(RSQLite)){
  install.packages("RSQLite")
  library(RSQLite)
}

# set working directory to arcproject-wq-processing folder
# To start with, check if we're on a dev machine or a production machine

# get the base folders
project_folder <- Sys.getenv("arcproject_code_path")  # get the main folder name - these variables set by Python before calling R
db_name <- Sys.getenv("arcproject_db_path")  # get the DB location

setwd(project_folder)

# source the heatplot graphing script
source("arcproject/scripts/heatplot.R")

# get all the water quality data for a given site
all_wq_reach <- function(connection, siteid){
  # select all water quality data for a specific
  statement = paste("select * from water_quality where site_id =", siteid, "and m_value IS NOT NULL")
  wq_by_site = dbGetQuery(con, statement) # water quality at selected site as dataframe
}

# generate a heatplot for a given slough and water quality variable
plot_wq_var <- function(connection, site_code, title, water_quality_var){

  # get the site id from the code
  statement = paste('select id from sites where code =', '"', site_code, '"', sep="")
  id = dbGetQuery(connection, statement)
  siteid = as.numeric(id$id)

  # load data for selected transect
  data <- all_wq_reach(connection, siteid)

  #check if there is actually data for the selected variable
  if(sum(!is.na(data[water_quality_var]))>0){
    p <- heatplot(data, "date_time", "m_value", water_quality_var, title)
  }else{print("Variable does not have enough data")}
  }

# save the plot to plots/heatplots folder
save_wq_plot <- function(plot_obj, site_code, var, output_folder){
  # save the plot to disk using the title as the filename
  name = paste(site_code, var, sep="_")
  # location to save plot
  filename <- paste(output_folder, "\\", name, ".png", sep="")

  # save the plot with ggsave()
  ggsave(filename, plot = plot_obj, device = "png", width = 7, height = 5, units="in")
}

##############################################
# get args if calling from subprocess
args <- commandArgs(trailingOnly=TRUE)
if(length(args) == 5){

  sitecode<-args[2]
  wqvar<-args[3]
  title<-args[4]
  output_folder<-args[5]

  # connect to the sqlite database
  con = dbConnect(SQLite(), dbname=db_name)
  p <- plot_wq_var(con, sitecode, title, wqvar)

  # save the plot to disk
  save_wq_plot(p, sitecode, wqvar, output_folder)
  
  # finally disconnect from the database
  dbDisconnect(con)

}else(stop("Not right number of arguments"))
#p
