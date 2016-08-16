# heatplot example
source("heatplot.R") # loads the heatplot function to create the graphs

# load data from csv
df <- read.csv(file="Arc_BKwqtCHL_example.csv", header=TRUE)

# variables
dateField <- "Date"
distanceField <- "Distance"
wqVariable <- "CHL"
title <- "BK - CHL"

# run function from heatplot.R to create the water quality heatplot
BK_CHL <- wq_heatplot(df, dateField, distanceField, wqVariable, title)

# view the plot
BK_CHL

# save the plot to disk using the title as the filename
filename <- paste(title, ".png")
ggsave(filename, plot=last_plot())