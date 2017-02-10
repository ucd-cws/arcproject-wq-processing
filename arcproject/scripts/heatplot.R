# function to create heatplot from a dataframe with date, distance, water quality info
.libPaths("C:\\arcproject-wq\\r_packages")  # add the project packages directory to the search path
library(ggplot2)

######################################################
unique_dates <- function(dataframe, dateField){
    df <- dataframe
    df[,dateField] <- as.Date(df[,dateField])
    df[,dateField] <- cut(df[,dateField], "month")
    df[,dateField] <- as.Date(df[,dateField]) + 15 # middle of the month
    unique <- unique(df[,dateField]) # get list of unique dates to use as breaks
}

yaxisformat <-function(x){
  x/1000
}

heatplot <- function(df, dateField, distanceField, wqVariable, title){
    # convert date_time to just date
    df[,dateField] <- as.Date(df[,dateField])
    df[,dateField] <- as.Date(df[,dateField])
    df[,dateField] <- cut(df[,dateField], "month")
    df[,dateField] <- as.Date(df[,dateField]) + 15 # middle of the month
   
    #convert WQ variable to num
    df[,wqVariable] <- as.numeric(df[,wqVariable])

    # get unique dates from dataframe
    date_breaks <- unique_dates(df, dateField)

    
    # plot using ggplot with geom_tile
    p <- ggplot(df, aes_string(x=dateField, y=distanceField, color=wqVariable)) +
      geom_point(pch=15, cex=3)+
      #geom_bar(width=31, stat="identity") + # makes widths equal to 31 days
      scale_color_gradientn(colours=c("blue","green","yellow","orange","red")) + # set color gradient
      ggtitle(title) +
      ylab("km")+
      scale_y_continuous(labels = yaxisformat) +
      scale_x_date(breaks=date_breaks, date_labels="%b - %Y")+ # format of x axis dates Mon - YEAR
      guides(fill = guide_colorbar(ticks = FALSE)) + # no tick marks
      theme_bw() +  # change theme simple with no axis or tick marks
      theme(panel.border = element_blank(), panel.grid.major = element_blank(),
            panel.grid.minor = element_blank(),
            #axis.title.y=element_blank(),
            #axis.text.y=element_blank(),
            #axis.ticks.y=element_blank(),
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

