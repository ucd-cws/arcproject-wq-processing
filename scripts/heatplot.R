# function to create heatplot from a dataframe with date, distance, water quality info
library(ggplot2)

# get parameters from subprocess
args <- commandArgs(trailingOnly=T)
print(args)

data <- as.character(args[1])
dateField <- as.character(args[2])
distanceField <- as.character(args[3])
wqVariable <- as.character(args[4])
title <- as.character(args[5])
output <- as.character(args[6])

########################

process_input_csv <- function(path_2_csv, dateField){
    df <- read.csv(path_2_csv, header=TRUE)
    # format date field
    #df[,dateField] <- as.Date(df[,dateField], "%m-%d-%Y")
    df[,dateField] <- as.Date(df[,dateField])
    
    #remove any NA from file
    df <- df[complete.cases(df),]
    return(df)
}

unique_dates <- function(dataframe, dateField){
    df <- dataframe
    unique <- unique(df[,dateField]) # get list of unique dates to use as breaks
}


heatplot <- function(df, dateField, distanceField, wqVariable, title){
    # plot using ggplot with geom_tile
    p <- ggplot(df, aes_string(dateField, distanceField, fill=wqVariable)) +
        geom_tile(width=31) + # makes widths equal to 31 days
        scale_fill_gradientn(colours=c("blue","green","yellow","orange","red")) + # set color gradient
        ggtitle(title) +
        scale_x_date(breaks=date_breaks, date_labels="%b - %Y")+ # format of x axis dates Mon - YEAR
        guides(fill = guide_colorbar(ticks = FALSE)) + # no tick marks
        theme_bw() +  # change theme simple with no axis or tick marks
        theme(panel.border = element_blank(), panel.grid.major = element_blank(),
              panel.grid.minor = element_blank(),axis.title.y=element_blank(),
              axis.text.y=element_blank(),
              axis.ticks.y=element_blank(),
              axis.ticks.x=element_blank(),
              axis.title.x = element_blank(),
              axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0.25), # x labels horizontal
              legend.position="top", # position of legend
              legend.direction="horizontal", # orientation of legend
              legend.title= element_blank() # no title for legend
        )

    p
}


# load csv as r dataframe
df <- process_input_csv(data, dateField)

# get unique dates from dataframe
date_breaks <- unique_dates(df, dateField)

hplot = heatplot(df, dateField, distanceField, wqVariable, title)
hplot

###########################################################################

# save the plot to disk using the title as the filename
#filename <- paste(title, ".png")
ggsave(output, plot = last_plot())
