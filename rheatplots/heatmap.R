####Production of heatmap of wq

library(plyr)
library(gplots)
library(grDevices)


#processing files
CHL <- read.csv("example_data/Arc_SBwqtCHL.csv")
CHLmat <- as.matrix(CHL)
CHLmat.r <-apply(CHLmat,2,rev)


##Set colors
col1 <- colorRampPalette(c("blue","green","yellow","orange","red"), space = "rgb")
col2 <- colorRampPalette(c("black","blue","green","yellow","orange","red"), space = "rgb")

#labels
Labels <- c("Mar13","Apr13","May13","Jun13","Jul13","Aug13","Sep13", "Oct13","Nov13","Dec13","Jan14","Feb14","Mar14","Apr14","May14","Jun14","Jul14","Aug14","Sep14","Oct14","Nov14","Dec14")


#heatmap.2() function is that it requires the data in a numerical matrix format in order to plot it

##Display heatmap
tiff(file="SB_CHL.tiff") #start to saving tiff
hmCHL <- heatmap.2(CHLmat.r,Rowv=NULL,Colv=NULL,dendrogram=c("none"),trace="none",density.info="none", main="SB_CHL", col=col1,labCol=labels,labRow=rev(Labels),cexRow=1.6,breaks=seq(0,35,by=0.025))
dev.off() #end to saving jpeg
