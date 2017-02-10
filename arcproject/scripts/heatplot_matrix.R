.libPaths("C:\\arcproject-wq\\r_packages")  # add the project packages directory to the search path

if (!require("gplots")) {
  install.packages("gplots", dependencies = TRUE)
  library(gplots)
}


data <- sh2m

mod_dates <- function(dataframe, dateField){
  df <- dataframe
  df[,dateField] <- as.Date(df[,dateField])
  df[,dateField] <- cut(df[,dateField], "month")
  #df[,dateField] <- as.Date(df[,dateField]) + 15 # middle of the month
  #unique <- unique(df[,dateField]) # get list of unique dates to use as breaks
  df
}

a <- mod_dates(data, 'date_time')
a
#m <- data.matrix(data)