# Heatplot using ggplot
library(ggplot2)
library(scales) 

# load in fake data to test
df <- read.csv(file="wq_data_along_fake_reach.csv", header=TRUE)

# format date field 
df$Date <- as.Date(df$Date, "%m/%d/%Y")

# plot using ggplot with geom_tile
p <- ggplot(df, aes(Date, Distance, fill=WQ_var3)) + 
  geom_tile(width=31) + # makes widths equal to 31 days 
  scale_fill_gradientn(colours=c("blue","green","yellow","orange","red")) + # set color gradient
  ggtitle("Demo transect")

p <- p + scale_x_date(breaks=df$Date, labels=date_format("%b - %Y")) # format of x axis dates Mon - YEAR

# change theme simple with no axis or tick marks
p <- p +
    guides(fill = guide_colorbar(ticks = FALSE)) +# no tick marks
    theme_bw() + 
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

# produce plot 
p 


