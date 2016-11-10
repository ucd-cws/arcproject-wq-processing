# function to create heatplot from a dataframe with date, distance, water quality info
library(ggplot2)


######################################################
unique_dates <- function(dataframe, dateField){
    df <- dataframe
    df[,dateField] <- as.Date(df[,dateField])
    unique <- unique(df[,dateField]) # get list of unique dates to use as breaks
}


heatplot <- function(df, dateField, distanceField, wqVariable, site_code, stations, stations_dist){
    # convert date_time to just date
    df[,dateField] <- as.Date(df[,dateField])
  
    # get unique dates from dataframe
    date_breaks <- unique_dates(df, dateField)
    
    # if missing values for stations return empty list
    if(missing(stations)){
      stations = c()
      stations_dist = c()
    }
  
    # plot using ggplot with geom_tile
    p <- ggplot(df, aes_string(dateField, distanceField, fill=wqVariable)) +
        geom_tile(width=31) + # makes widths equal to 31 days
        scale_fill_gradientn(colours=c("blue","green","yellow","orange","red")) + # set color gradient
        ggtitle(paste(toupper(wqVariable), "-", toupper(site_code))) +
        scale_y_continuous(breaks=stations_dist, labels = stations) +
        scale_x_date(breaks=date_breaks, date_labels="%b - %Y")+ # format of x axis dates Mon - YEAR
        guides(fill = guide_colorbar(ticks = FALSE)) + # no tick marks
        theme_bw() +  # change theme simple with no axis or tick marks
        theme(panel.border = element_blank(), panel.grid.major = element_blank(),
              panel.grid.minor = element_blank(),axis.title.y=element_blank(),
              #axis.text.y=element_blank(),
              axis.ticks.y=element_blank(),
              axis.ticks.x=element_blank(),
              axis.title.x = element_blank(),
              axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0.25), # x labels horizontal
              legend.position="top", # position of legend
              legend.direction="horizontal", # orientation of legend
              legend.title= element_blank(), # no title for legend
              legend.key.size = unit(1.5, "cm") # size of legend
        )
    p
}




