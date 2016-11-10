library("RSQLite")

# set working directory to arcproject-wq-processing folder
project_folder = "~/arcproject-wq-processing"
setwd(project_folder)

# source the heatplot graphing script
source("scripts/heatplot.R")

# connect to the sqlite database
con = dbConnect(SQLite(), dbname="wqdb.sqlite")

# get the slough reaches as a data.frame
sites_df = dbGetQuery(con,'select * from sites')

for (i in 1:nrow(sites_df)){
  site_code = sites_df$code
  
  # TODO get vertical profile site IDs and m_values for given site_code
  
  # select all water quality data for a specific site
  statement = paste("select * from water_quality where site_id = ", sites_df$id, "and m_value IS NOT NULL")
  wq_by_site = dbGetQuery(con,  statement)
  
  
  # iterate through all the water quality variables creating heatmaps
  
  wq_var = c("temp", "ph", "sp_cond", "salinity", "par", "rpar", "turbidity_sc", "chl") # not all wq vars included
  
  for(var in wq_var){
    print(var)
    # TODO - catch the wq_vars that don't have any data
    p <- heatplot(wq_by_site, "date_time", "m_value", var, site_code, c("SG1", "SG2"), c(500, 700))
    # save the plot to disk using the title as the filename
    name = paste(site_code, var, sep="_")
    filename <- paste("plots/heatplots/",name, ".png", sep = "")
    ggsave(filename, plot = last_plot())
  }
}

# finally disconnect from the database
dbDisconnect(con)
