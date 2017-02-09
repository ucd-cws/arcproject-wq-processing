
######################################################################
##### Correction of wq data using lab-derived chlorophyll values #####
######################################################################


######################################################################

#    Notes:

#    Make sure you have all your files where they need to be. This includes a Monthly Transect Import 
#    file, your Daily Gain files (gn1/10/100 and truncated files) and an updated lab value file. Files 
#    need to be saved as .CSV and formatted correctly. Site from Daily Gain file and lab value must match.

#    This code ultimately generates a monthly import file with extra columns: corrected chl gn 1, gn 10, and gn 100.

#    Join to monthly summary pnt file in ArcMap
#    Export as Arc_MMMYYYY_WQt_gn1_gn10_gn100_cor.shp
#    Run a near from Arc toolbox. Input Feature is point final layer and Near Feature is monthly wqdata. 
#    Search Radius is 250 meters. Once the Near is done running, you will need to do a join. 
#    Right click Monthly WQt summary file->Joins and Relates->Join.-> (1.) Select "Join attributes from 
#    a table") 1. NEAR_FID 2. Monthly WQ data 3. FID. Make sure that "Keep only matching records" is selected.
    

######################################################################

##Run this section once per day.

#Imports monthly summary wqt file.
wqt <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Raw_Data_Files/Monthly_Transect_Files/Arc_MMM_YYYY_WQt_Import.csv", header=TRUE, stringsAsFactors=FALSE)
#Filters bad values out.
wqtf <- wqt[which(wqt$Sal > 0 & wqt$CHL < 2.000e+06 & wqt$TurbSC<3000),]
#Subsets data by day. First set is for GN10 and the 2nd set is for GN1
wqtfMMDDYY <- subset(wqtf,wqt$Date=="MM/DD/YYYY")
wqtfMMDDYY_2 <- subset(wqtf,wqt$Date=="MM/DD/YYY")



#Opens GN10 and GN1 daily profile Files.
wq_gn10 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Raw_Data_Files/Daily_Gain_Files/Gain10_trunc/Arc_MMDDYY_wqp_gn10_trunc.csv", header=TRUE, stringsAsFactors=FALSE) ###OPEN DAILY GAIN 10 file 
wq_gn1 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Raw_Data_Files/Daily_Gain_Files/Gain1_trunc/Arc_MMDDYY_wqp_gn1_trunc.csv", header=TRUE, stringsAsFactors=FALSE) ###OPEN DAILY GAIN 1 file 
#Creates and generates Date_Site column.
wq_gn10$SiteID <- paste(wq_gn10$Site,wq_gn10$Date,sep="_")
#filters bad values out and any data taken below 1m.
wqf_gn10 <- wq[which(wq_gn10$DEP25 < 1 & wq_gn10$Sal > 0 & wq_gn10$CHL < 2.000e+06 & wq_gn10$CHL > 0 & wq_gn10$TurbSC<3000),]
#Aggregates by SiteID and averages the values.
wqchlagg_gn10 <-aggregate(wqf_gn10, by=list(wqf$SiteID),FUN=mean, na.rm=FALSE,stringsAsFactors=FALSE)
#Renames columns.
colnames(wqchlagg_gn10)[colnames(wqchlagg_gn10) == "SiteID"] <- "NA"
colnames(wqchlagg_gn10)[colnames(wqchlagg_gn10) == "Group.1"] <- "SiteID"
#Opens chl lab data.
chlalab <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Raw_Data_Files/Lab_Values/DahlgrenData_StandardArcOnlyForRegressions_080514.csv",stringsAsFactors=FALSE)
#Joins 1m means with the lab values based on SiteID.
wqchl_gn10 <- merge(wqchlagg_gn10,chlalab,by="SiteID")
#Renames column.
colnames(wqchl_gn10)[colnames(wqchl_gn10) == "Chlorophyll.a"] <- "CHL2"
#Saves and reopens file.
write.table(wqchl_gn10, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn10_wqchl.csv") 
wqchl_gn10 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn10_wqchl.csv", header=TRUE,sep=" ", row.names=1)

#start to saving plot as jpeg, dev.off() to end
jpeg(file="X:/ArcProject/Arc_Heatmaps/DailyScatterPlots/MMDDYY_gn10.jpg") 
#Creates regression of Lab vs field value. CHL2 = lab = y, CHL = field = x)
chlrgrsn_gn10 <- lm(wqchl_gn10$CHL2~wqchl_gn10$CHL)
coeffs_gn10 = coefficients(chlrgrs_ngn10); coeffs_gn10 
a_gn10 <- signif(coef(chlrgrsn_gn10)[1], digits = 3)
b_gn10 <- signif(coef(chlrgrsn_gn10)[2], digits = 3)
r2_coeffs_gn10 <- paste("r^2 = ",summary(chlrgrsn_gn10, digits = 3)$r.squared," ,y = ",b_gn10,"x + ",a_gn10, sep="")
plot(wqchl_gn10$CHL,wqchl_gn10$CHL2,main="Arc_MMDDYY_gn10", ylab="Lab_chl",xlab="Field_chl", sub=r2_coeffs_gn10)
abline(chlrgrsn_gn10)
dev.off() #end to saving jpeg
#Saves regression coefficients.
write.csv(coeffs_gn10, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn10_coeffs.csv")
#Saves r^2 value
write.csv(summary(chlrgrsn_gn10)$r.squared, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn10_r2.csv")

#Creates a column and applies the regression to daily proFiles.
wq_gn10$NewCHL <- paste(NewCHL=coeffs_gn10[1] + coeffs_gn10[2]*wq_gn10$CHL)
#Saves a daily wqt file.
write.csv(wq_gn10, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn10_wqpchl.csv")
#Creates a column and applies regression to daily transect file.
wqtfMMDDYY_gn10$NewCHL <- paste(NewCHL=coeffs_gn10[1] + coeffs_gn10[2]*wqtfMMDDYY_gn10$CHL)
write.csv(wqtfMMDDYY_gn10, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn10_wqtchl.csv")

##Second set, same as above. This is to work up the GN1 data.
wq_gn1$SiteID <- paste(wq_gn1$Site,wq_gn1$Date,sep="_")
wqf_gn1 <- wq_gn1[which(wq_gn1$DEP25 < 1 & wq_gn1$Sal > 0 & wq_gn1$CHL < 2.000e+06 & wq_gn1$CHL > 0 & wq_gn1$TurbSC<3000),]                              
wqchlagg_gn1 <-aggregate(wqf_gn1, by=list(wqf_gn1$SiteID),FUN=mean, na.rm=FALSE,stringsAsFactors=FALSE) ##added stringsAsFactors=FALSE
colnames(wqchlagg_gn1)[colnames(wqchlagg_gn1) == "SiteID"] <- "NA"
colnames(wqchlagg_gn1)[colnames(wqchlagg_gn1) == "Group.1"] <- "SiteID"
chlalab <- read.csv("X:/ArcProject/Arc_Heatmaps/DahlgrenData_StandardArcOnlyForRegressions_080514.csv")
wqchl_gn1 <- merge(wqchlagg2,chlalab,by="SiteID",stringsAsFactors=FALSE)
colnames(wqchl_gn1)[colnames(wqchl_gn1) == "Chlorophyll.a"] <- "CHL2"
write.table(wqchl_gn1, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn1_wqchl.csv")  ##got rid of separator
wqchl_gn1 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn1_wqchl.csv", header=TRUE,sep=" ", row.names=1)  ## made separator " " instead of "/t"
jpeg(file="X:/ArcProject/Arc_Heatmaps/DailyScatterPlots/MMDDYY_gn1.jpg") #start to saving jpeg
chlrgrsn_gn1 <- lm(wqchl_gn1$CHL2~wqchl_gn1$CHL)
coeffs_gn1 = coefficients(chlrgrsn_gn1); coeffs_gn1 
a_gn1 <- signif(coef(chlrgrsn_gn1)[1], digits = 3)
b_gn1 <- signif(coef(chlrgrsn_gn1)[2], digits = 3)
r2_coeffs_gn1 <- paste("r^2 = ",summary(chlrgrsn_gn1, digits = 3)$r.squared," ,y = ",b_gn1,"x + ",a_gn1, sep="")
plot(wqchl_gn1$CHL,wqchl_gn1$CHL2,main="Arc_MMDDYY_gn1", ylab="Lab_chl",xlab="Field_chl", sub=r2_coeffs_gn1)
abline(chlrgrsn_gn1)
dev.off() #end to saving jpeg
write.csv(coeffs_gn1, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn1_coeffs.csv")
write.csv(summary(chlrgrsn_gn1)$r.squared, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn1_r2.csv")


chlrgrsn_gn1 <- lm(wqchl_gn1$CHL2~wqchl_gn1$CHL)
plot(wqchl_gn1$CHL,wqchl_gn1$CHL2)
abline(chlrgrsn_gn1)
coeffs_gn1 = coefficients(chlrgrsn_gn1); coeffs_gn1 


write.csv(coeffs_gn1, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn1_coeffs.csv")
wq_gn1$NewCHL <- paste(NewCHL=coeffs_gn1[1] + coeffs_gn1[2]*wq2$CHL)
write.csv(wq_gn1, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn1_wqpchl.csv")

wqtfMMDDYY_gn1$NewCHL <- paste(NewCHL=coeffs_gn1[1] + coeffs_gn1[2]*wqtfMMDDYY_gn1$CHL)
write.csv(wqtfMMDDYY_gn1, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn1_wqtchl.csv")

##Run this code once, and only when you have all your worked up daily files.
#Stacks the Files according to row name.
MMMYYYY_wqt_gn1 <- rbind(read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn1_wqtchl.csv"),
                         read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn1_wqtchl.csv"),    
                         read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn1_wqtchl.csv"))
MMMYYYY_wqt_gn10 <- rbind(read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn10_wqtchl.csv"),
                          read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn10_wqtchl.csv"),
                          read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_MMDDYY_gn10_wqtchl.csv"))
#Saves Files.
write.csv(MMMYYYY_wqt_gn1, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_MMMYYYY_gn1_wqtchl.csv")
write.csv(MMMYYYY_wqt_gn10, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_MMMYYYY_gn10_wqtchl.csv")
#Renames columns.
colnames(MMMYYYY_wqt_gn1)[colnames(MMMYYYY_wqt_gn1) == "NewCHL"] <- "NewCHL_gn1"
colnames(MMMYYYY_wqt_gn10)[colnames(MMMYYYY_wqt_gn10) == "NewCHL"] <- "NewCHL_gn10"
#Subsets data in preparation for a merge.
MMMYYYY_wqt_gn10_subset <- subset(MMMYYYY_wqt_gn10, select=c(Date_Time,NewCHL_gn10))
#Merges GN1 and GN10 data based on Date_Time column
MMMYYYY_wqt_gn1_gn10 <- merge(MMMYYYY_wqt_gn1,MMMYYYY_wqt_gn10_subset,by="Date_Time")
#Saves wqt file with corrected chl (both GN1 and GN10).
write.csv(MMMYYYY_wqt_gn1_gn10, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_MMMYYYY_gn1_gn10_wqtchl.csv")
View(MMMYYYY_wqt_gn1_gn10)



########################
##### Working Code #####
########################

# set working directory to this folder
setwd("~/arcproject-wq-processing/scripts/R")


#Run for each day

wqt <- read.csv("test_data/Arc_Sep2014_WQt_Import.csv", header=TRUE, stringsAsFactors=FALSE)
wqtf <- wqt[which(wqt$Sal > 0 & wqt$CHL < 2.000e+06 & wqt$TurbSC<3000),]
wqtf091514_gn10 <- subset(wqtf,wqt$Date=="9/15/2014")
wqtf091514_gn1 <- subset(wqtf,wqt$Date=="9/15/2014")
wqtf091514_gn100 <- subset(wqtf,wqt$Date=="9/15/2014")

wq_gn100 <- read.csv("test_data/Arc_091514_wqp_gn100_trunc.csv", header=TRUE, stringsAsFactors=FALSE) ###OPEN DAILY GAIN 100 file
wq_gn10 <- read.csv("test_data/Arc_091514_wqp_gn10_trunc.csv", header=TRUE, stringsAsFactors=FALSE) ###OPEN DAILY GAIN 10 file 
wq_gn1 <- read.csv("test_data/Arc_091514_wqp_gn1_trunc.csv", header=TRUE, stringsAsFactors=FALSE) ###OPEN DAILY GAIN 1 file 



wq_gn10$SiteID <- paste(wq_gn10$Site,wq_gn10$Date,sep="_")
wqf_gn10 <- wq_gn10[which(wq_gn10$DEP25 < 1 & wq_gn10$Sal > 0 & wq_gn10$CHL < 2.000e+06 & wq_gn10$CHL > 0 & wq_gn10$TurbSC<3000),]                              
wqchlagg_gn10 <-aggregate(wqf_gn10, by=list(wqf_gn10$SiteID),FUN=mean, na.rm=FALSE,stringsAsFactors=FALSE) ##added stringsAsFactors=FALSE
colnames(wqchlagg_gn10)[colnames(wqchlagg_gn10) == "SiteID"] <- "NA"
colnames(wqchlagg_gn10)[colnames(wqchlagg_gn10) == "Group.1"] <- "SiteID"

chlalab <- read.csv("test_data/Arc_Project_chl_values_July14_Dec14.csv",stringsAsFactors=FALSE)
wqchl_gn10 <- merge(wqchlagg_gn10,chlalab,by="SiteID")
colnames(wqchl_gn10)[colnames(wqchl_gn10) == "Chlorophyll.a"] <- "CHL2"
write.table(wqchl_gn10, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn10_wqchl.csv")  ##got rid of separator
wqchl_gn10 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn10_wqchl.csv", header=TRUE,sep=" ", row.names=1)  ## made separator " " instead of "/t"

jpeg(file="091514_gn10.jpg")
chlrgrsn_gn10 <- lm(wqchl_gn10$CHL2~wqchl_gn10$CHL)
coeffs_gn10 <- coefficients(chlrgrsn_gn10); coeffs_gn10
a_gn10 <- signif(coef(chlrgrsn_gn10)[1], digits = 3)
b_gn10 <- signif(coef(chlrgrsn_gn10)[2], digits = 3)
r2_coeffs_gn10 <- paste("r^2 = ",summary(chlrgrsn_gn10, digits = 3)$r.squared," ,y = ",b_gn10,"x + ",a_gn10, sep="")
plot(wqchl_gn10$CHL,wqchl_gn10$CHL2,main="Arc_091514_gn10", ylab="Lab_chl",xlab="Field_chl", sub=r2_coeffs_gn10)
abline(chlrgrsn_gn10)
dev.off()


write.csv(coeffs_gn10, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn10_coeffs.csv")
write.csv(summary(chlrgrsn_gn10)$r.squared, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn10_r2.csv")
wq_gn10$NewCHL <- paste(NewCHL=coeffs_gn10[1] + coeffs_gn10[2]*wq_gn10$CHL)
write.csv(wq_gn10, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn10_wqpchl.csv")
wqtf091514_gn10$NewCHL <- paste(NewCHL=coeffs_gn10[1] + coeffs_gn10[2]*wqtf091514_gn10$CHL)
write.csv(wqtf091514_gn10, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn10_wqtchl.csv")
wq_gn1$SiteID <- paste(wq_gn1$Site,wq_gn1$Date,sep="_")
wqf_gn1 <- wq_gn1[which(wq_gn1$DEP25 < 1 & wq_gn1$Sal > 0 & wq_gn1$CHL < 2.000e+06 & wq_gn1$CHL > 0 & wq_gn1$TurbSC<3000),]                              
wqchlagg_gn1 <-aggregate(wqf_gn1, by=list(wqf_gn1$SiteID),FUN=mean, na.rm=FALSE,stringsAsFactors=FALSE) ##added stringsAsFactors=FALSE
colnames(wqchlagg_gn1)[colnames(wqchlagg_gn1) == "SiteID"] <- "NA"
colnames(wqchlagg_gn1)[colnames(wqchlagg_gn1) == "Group.1"] <- "SiteID"
wqchl_gn1 <- merge(wqchlagg_gn1,chlalab,by="SiteID",stringsAsFactors=FALSE)
colnames(wqchl_gn1)[colnames(wqchl_gn1) == "Chlorophyll.a"] <- "CHL2"
write.table(wqchl_gn1, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn1_wqchl.csv")  ##got rid of separator
wqchl_gn1 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn1_wqchl.csv", header=TRUE,sep=" ", row.names=1)  ## made separator " " instead of "/t"
jpeg(file="X:/ArcProject/Arc_Heatmaps/DailyScatterPlots/091514_gn1.jpg")
chlrgrsn_gn1 <- lm(wqchl_gn1$CHL2~wqchl_gn1$CHL)
coeffs_gn1 = coefficients(chlrgrsn_gn1); coeffs_gn1
a_gn1 <- signif(coef(chlrgrsn_gn1)[1], digits = 3)
b_gn1 <- signif(coef(chlrgrsn_gn1)[2], digits = 3)
r2_coeffs_gn1 <- paste("r^2 = ",summary(chlrgrsn_gn1, digits = 3)$r.squared," ,y = ",b_gn1,"x + ",a_gn1, sep="")
plot(wqchl_gn1$CHL,wqchl_gn1$CHL2,main="Arc_091514_gn1", ylab="Lab_chl",xlab="Field_chl", sub=r2_coeffs_gn1)
abline(chlrgrsn_gn1)
dev.off()
write.csv(coeffs_gn1, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn1_coeffs.csv")
write.csv(summary(chlrgrsn_gn1)$r.squared, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn1_r2.csv")
wq_gn1$NewCHL <- paste(NewCHL=coeffs_gn1[1] + coeffs_gn1[2]*wq_gn1$CHL)
write.csv(wq_gn1, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn1_wqpchl.csv")
wqtf091514_gn1$NewCHL <- paste(NewCHL=coeffs_gn1[1] + coeffs_gn1[2]*wqtf091514_gn1$CHL)
write.csv(wqtf091514_gn1, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn1_wqtchl.csv")

wq_gn100$SiteID <- paste(wq_gn100$Site,wq_gn100$Date,sep="_")
wqf_gn100 <- wq_gn100[which(wq_gn100$DEP25 < 1 & wq_gn100$Sal > 0 & wq_gn100$CHL < 2.000e+06 & wq_gn100$CHL > 0 & wq_gn100$TurbSC<3000),]                              
wqchlagg_gn100 <-aggregate(wqf_gn100, by=list(wqf_gn100$SiteID),FUN=mean, na.rm=FALSE,stringsAsFactors=FALSE) ##added stringsAsFactors=FALSE
colnames(wqchlagg_gn100)[colnames(wqchlagg_gn100) == "SiteID"] <- "NA"
colnames(wqchlagg_gn100)[colnames(wqchlagg_gn100) == "Group.1"] <- "SiteID"
wqchl_gn100 <- merge(wqchlagg_gn100,chlalab,by="SiteID",stringsAsFactors=FALSE)
colnames(wqchl_gn100)[colnames(wqchl_gn100) == "Chlorophyll.a"] <- "CHL2"
write.table(wqchl_gn100, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn100_wqchl.csv")  ##got rid of separator
wqchl_gn100 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn100_wqchl.csv", header=TRUE,sep=" ", row.names=1)  ## made separator " " instead of "/t"
jpeg(file="X:/ArcProject/Arc_Heatmaps/DailyScatterPlots/091514_gn100.jpg")
chlrgrsn_gn100 <- lm(wqchl_gn100$CHL2~wqchl_gn100$CHL)
coeffs_gn100 = coefficients(chlrgrsn_gn100); coeffs_gn100
a_gn100 <- signif(coef(chlrgrsn_gn100)[1], digits = 3)
b_gn100 <- signif(coef(chlrgrsn_gn100)[2], digits = 3)
r2_coeffs_gn100 <- paste("r^2 = ",summary(chlrgrsn_gn100, digits = 3)$r.squared," ,y = ",b_gn100,"x + ",a_gn100, sep="")
plot(wqchl_gn100$CHL,wqchl_gn100$CHL2,main="Arc_091514_gn100", ylab="Lab_chl",xlab="Field_chl", sub=r2_coeffs_gn100)
abline(chlrgrsn_gn100)
dev.off()
write.csv(coeffs_gn100, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn100_coeffs.csv")
write.csv(summary(chlrgrsn_gn100)$r.squared, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn100_r2.csv")
wq_gn100$NewCHL <- paste(NewCHL=coeffs_gn100[1] + coeffs_gn100[2]*wq_gn100$CHL)
write.csv(wq_gn100, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn100_wqpchl.csv")
wqtf091514_gn100$NewCHL <- paste(NewCHL=coeffs_gn100[1] + coeffs_gn100[2]*wqtf091514_gn100$CHL)
write.csv(wqtf091514_gn100, "X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn100_wqtchl.csv")

#####
##Individually change dates here
#####

Sep2014_wqt_gn1 <- rbind(read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn1_wqtchl.csv"),
                         read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_071014_gn1_wqtchl.csv"),    
                         read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_071714_gn1_wqtchl.csv"))
Sep2014_wqt_gn10 <- rbind(read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn10_wqtchl.csv"),
                          read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_071014_gn10_wqtchl.csv"),
                          read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_071714_gn10_wqtchl.csv"))
Sep2014_wqt_gn100 <- rbind(read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_091514_gn100_wqtchl.csv"),
                           read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_071014_gn100_wqtchl.csv"),
                           read.csv("X:/ArcProject/Arc_Heatmaps/Arc_Intermediate_Files/Arc_071714_gn100_wqtchl.csv"))

write.csv(Sep2014_wqt_gn1, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Sep2014_gn1_wqtchl.csv")
write.csv(Sep2014_wqt_gn10, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Sep2014_gn10_wqtchl.csv")
write.csv(Sep2014_wqt_gn100, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Sep2014_gn100_wqtchl.csv")
colnames(Sep2014_wqt_gn1)[colnames(Sep2014_wqt_gn1) == "NewCHL"] <- "NewCHL_gn1"
colnames(Sep2014_wqt_gn10)[colnames(Sep2014_wqt_gn10) == "NewCHL"] <- "NewCHL_gn10"
colnames(Sep2014_wqt_gn100)[colnames(Sep2014_wqt_gn100) == "NewCHL"] <- "NewCHL_gn100"
Sep2014_wqt_gn10_subset <- subset(Sep2014_wqt_gn10, select=c(Date_Time,NewCHL_gn10))
Sep2014_wqt_gn100_subset <- subset(Sep2014_wqt_gn100, select=c(Date_Time,NewCHL_gn100))
Sep2014_wqt_gn1_gn10 <- merge(Sep2014_wqt_gn1,Sep2014_wqt_gn10_subset,by="Date_Time")
Sep2014_wqt_gn1_gn10_gn100 <- merge(Sep2014_wqt_gn1_gn10,Sep2014_wqt_gn100_subset,by="Date_Time")

write.csv(Sep2014_wqt_gn1_gn10_gn100, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Sep2014_gn1_gn10_gn100_wqtchl.csv")
View(Sep2014_wqt_gn1_gn10_gn100)

