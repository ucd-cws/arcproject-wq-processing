library("RSQLite")

# set working directory to arcproject-wq-processing folder
project_folder = "~/arcproject-wq-processing"
setwd(project_folder)

# source the heatplot graphing script
source("scripts/heatplot.R")

# connect to the sqlite database
con = dbConnect(SQLite(), dbname="wqdb.sqlite")


# get the vertical gain ref points for slough given the transect site_code.
# Returns list of profile site names and m_values 
vert_gain_m_locs <- function(connection, siteid){
  statement = paste("select * from profile_sites where site_id = ", siteid, "and m_value IS NOT NULL")
  v = dbGetQuery(connection,  statement)
  
  station_names = v$profile_name # TODO check the actual field name in profile_sites 
  station_meas = v$m_value # TODO check the actual field name in profile_sites 
  
  stations = list(station_names, station_meas) # r can only return 1 thing at a time so zip up as a list of lists
} 


# get all the water quality data for a given slough site
all_wq_reach <- function(connection, siteid){
  # select all water quality data for a specific  
  statement = paste("select * from water_quality where site_id =", siteid, "and m_value IS NOT NULL")
  
  wq_by_site = dbGetQuery(con, statement) # water quality at selected site as dataframe
}


# generate a heatplot for a given slough and water quality variable
plot_wq_var <- function(connection, siteid, sitename, water_quality_var){
  # get the locations for the vertical gain profiles along the transect
  vert_profile_spots <- vert_gain_m_locs(connection, siteid)
  
  # load data for selected transect
  data <- all_wq_reach(connection, siteid)
  
  # check if there is actually data for the selected variable
  if(sum(!is.na(data[water_quality_var]))>0){
  p <- heatplot(data, "date_time", "m_value", water_quality_var, sitename, vert_profile_spots[[1]], vert_profile_spots[[2]])
  }
  else{print("Variable does not have enough data")}
  }


# save the plot to plots/heatplots folder
save_wq_plot <- function(plot_obj, site_code, var){
  # save the plot to disk using the title as the filename
  name = paste(site_code, var, sep="_")
  # location to save plot
  filename <- paste("plots/heatplots/",name, ".png", sep = "")
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
    if(is.character(p)){print("Skiping...")}
    
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


# wq list
wq_list = c("temp","ph","sp_cond","salinity", "dissolved_oxygen","dissolved_oxygen_percent", 
            "dep_25", "par", "rpar","turbidity_sc","chl", "chl_volts","chl_corrected","corrected_gain")


# batch generates all heatplots to plots/heatplots/{sitecode}_{variable}.png
generate_all(con, wq_list)


# finally disconnect from the database
dbDisconnect(con)
