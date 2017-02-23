library("RSQLite")

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
save_wq_plot <- function(plot_obj, site_code, var){
  # save the plot to disk using the title as the filename
  name = paste(site_code, var, sep="_")
  # location to save plot
  filename <- paste(project_folder, "/arcproject/plots/heatplots/",name, ".png", sep = "")
  # save the plot with ggsave()
  ggsave(filename, plot = plot_obj)
}


# generate the heatplots for a single water quality variable for all transects
all_reaches_for_one_wq <- function(connection, wq_variable){
  # get the slough reaches as a data.frame
  sites_df = dbGetQuery(connection,'select * from sites')

  # loop through all the transects
  for (i in 1:nrow(sites_df)){

    # infomation about the transect
    site_id = sites_df$id[i]
    site_name = sites_df$name[i]
    site_code = sites_df$code[i]

    # plot the water quality varaible for the transect
    p <- plot_wq_var(connection, site_id, site_name, wq_variable)

    # saves the plot
    save_wq_plot(p, site_code, wq_variable)
  }
}


# generate the heaplots for a list of water quality variable along a single transect
heatplots_singletransect <- function(connection, siteid, list_wq_vars){
  # get the slough reaches as a data.frame
  sites_df = dbGetQuery(connection, paste('select * from sites where id =', siteid))

  # get information about the transect
  site_id = sites_df$id[1]
  site_name = sites_df$name[1]
  site_code = sites_df$code[1]

  # loop through the water quality variables
  for(i in 1:length(list_wq_vars)){
    # create the plot for a single water quality variable
    p <- plot_wq_var(connection, site_id, site_name, list_wq_vars[i])

    # check if the result is an error message or plot
    if(is.character(p)){print("Skipping...")}

    # save plot
    else{save_wq_plot(p, site_code, list_wq_vars[i])}
    }
  }


# generate all the heatplots for the list of water quality variable
generate_all <- function(connection,list_wq_vars){
  # get the slough reaches as a data.frame
  sites_df = dbGetQuery(connection,'select * from sites')

  # loop through all the transects
  for (i in 1:nrow(sites_df)){
    site_id = sites_df$id[i]

    # generate all heatplots for the selected transect
    heatplots_singletransect(connection, site_id, list_wq_vars)
  }
}

##############################################
# get argvs if calling from script
#args<- c("junk", 'CC', 'ph', 'Title')
args <- commandArgs(trailingOnly=TRUE)
if(length(args) == 4){

  siteid<-args[2]
  wqvar<-args[3]
  title<-args[4]

  # connect to the sqlite database
  con = dbConnect(SQLite(), dbname=db_name)

  p <- plot_wq_var(con, siteid, title, wqvar)

  # save the plot to disk using the title as the filename
  # saves the plot
  save_wq_plot(p, siteid, wqvar)

  # finally disconnect from the database
  dbDisconnect(con)

}else(stop("Not right number of arguments"))
p
