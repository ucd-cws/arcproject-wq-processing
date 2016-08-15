
##################################
##### Final CHL heatmap prep #####
##################################

#this script creates a single file (Arc_Final_CHL_All.csv) that has the final chl values

#packages
library(plyr)
library(gplots)
library(grDevices)

##open each monthly file, daily r2 values, and template to facilitate joins
r2 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_r2.csv")
Final_CHL <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Final_CHL.csv",stringsAsFactors=FALSE)
Dec12 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2012_WQt_gn0_cor_snapped.csv",stringsAsFactors=FALSE)
Jan13 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Jan2013_WQt_gn0_cor_snapped.csv",stringsAsFactors=FALSE)
Feb13 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Feb2013_WQt_gn0_cor_snapped.csv",stringsAsFactors=FALSE)
Mar13 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Mar2013_WQt_gn0_cor_snapped.csv",stringsAsFactors=FALSE)
Apr13 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Apr2013_WQt_gn0_cor_snapped.csv",stringsAsFactors=FALSE)
May13 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_May2013_WQt_gn0_cor_snapped.csv",stringsAsFactors=FALSE)
Jun13 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Jun2013_WQt_gn0_cor_snapped.csv",stringsAsFactors=FALSE)
Jul13 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Jul2013_WQt_gn0_cor_snapped.csv",stringsAsFactors=FALSE)
Aug13 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Aug2013_WQt_gn1_gn10_cor_snapped.csv",stringsAsFactors=FALSE)
Sep13 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Sep2013_WQt_gn1_gn10_cor_snapped.csv",stringsAsFactors=FALSE)
Oct13 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Oct2013_WQt_gn1_gn10_cor_snapped.csv",stringsAsFactors=FALSE)
Nov13 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Nov2013_WQt_gn1_gn10_cor_snapped.csv",stringsAsFactors=FALSE)
Dec13 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2013_WQt_gn1_gn10_cor_snapped.csv",stringsAsFactors=FALSE)
Jan14 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Jan2014_WQt_gn1_gn10_cor_snapped.csv",stringsAsFactors=FALSE)
Feb14 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Feb2014_WQt_gn1_gn10_cor_snapped.csv",stringsAsFactors=FALSE)
Mar14 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Mar2014_WQt_gn1_gn10_cor_snapped.csv",stringsAsFactors=FALSE)
Apr14 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Apr2014_WQt_gn1_gn10_cor_snapped.csv",stringsAsFactors=FALSE)
May14 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_May2014_WQt_gn1_gn10_cor_snapped.csv",stringsAsFactors=FALSE)
Jun14 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Jun2014_WQt_gn1_gn10_cor_snapped.csv",stringsAsFactors=FALSE)
Jul14 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Jul2014_WQt_gn1_gn10_cor_snapped.csv",stringsAsFactors=FALSE)
Aug14 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Aug2014_WQt_gn1_gn10_gn100_cor_snapped.csv",stringsAsFactors=FALSE)
Sep14 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Sep2014_WQt_gn1_gn10_gn100_cor_snapped.csv",stringsAsFactors=FALSE)
Oct14 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Oct2014_WQt_gn1_gn10_gn100_cor_snapped.csv",stringsAsFactors=FALSE)
Nov14 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Nov2014_WQt_gn1_gn10_gn100_cor_snapped.csv",stringsAsFactors=FALSE)
Dec14 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Dec2014_WQt_gn1_gn10_gn100_cor_snapped.csv",stringsAsFactors=FALSE)

##subset data (only need Date, CHL, RID, and MEAS)
Dec12<- subset(Dec12, select=c(RID, MEAS, Date, Dec12_CHL, Dec12_NewCHL))
Jan13<- subset(Jan13, select=c(RID, MEAS, Date, Jan13_CHL, Jan13_NewCHL))
Feb13<- subset(Feb13, select=c(RID, MEAS, Date, Feb13_CHL, Feb13_NewCHL))
Mar13<- subset(Mar13, select=c(RID, MEAS, Date, Mar13_CHL, Mar13_NewCHL))
Apr13<- subset(Apr13, select=c(RID, MEAS, Date, Apr13_CHL, Apr13_NewCHL))
May13<- subset(May13, select=c(RID, MEAS, Date, May13_CHL, May13_NewCHL))
Jun13<- subset(Jun13, select=c(RID, MEAS, Date, Jun13_CHL, Jun13_NewCHL))
Jul13<- subset(Jul13, select=c(RID, MEAS, Date, Jul13_CHL, Jul13_NewCHL))
Aug13<- subset(Aug13, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1))
Sep13<- subset(Sep13, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1))
Oct13<- subset(Oct13, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1))
Nov13<- subset(Nov13, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1))
Dec13<- subset(Dec13, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1))
Jan14<- subset(Jan14, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1))
Feb14<- subset(Feb14, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1))
Mar14<- subset(Mar14, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1))
Apr14<- subset(Apr14, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1))
May14<- subset(May14, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1))
Jun14<- subset(Jun14, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1))
Jul14<- subset(Jul14, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1))
Aug14<- subset(Aug14, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1 ,NewCHL_g_2))
Sep14<- subset(Sep14, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1 ,NewCHL_g_2))
Oct14<- subset(Oct14, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1 ,NewCHL_g_2))
Nov14<- subset(Nov14, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1 ,NewCHL_g_2))
Dec14<- subset(Dec14, select=c(RID, MEAS, Date, CHL,NewCHL_gn1 ,NewCHL_g_1 ,NewCHL_g_2))

##takes care of significant figure issue for join using slough distance
Final_CHL$MEAS<-paste(signif(Final_CHL$MEAS, digits=5))
Dec12$MEAS<-paste(signif(Dec12$MEAS, digits=5))
Jan13$MEAS<-paste(signif(Jan13$MEAS, digits=5))
Feb13$MEAS<-paste(signif(Feb13$MEAS, digits=5))
Mar13$MEAS<-paste(signif(Mar13$MEAS, digits=5))
Apr13$MEAS<-paste(signif(Apr13$MEAS, digits=5))
May13$MEAS<-paste(signif(May13$MEAS, digits=5))
Jun13$MEAS<-paste(signif(Jun13$MEAS, digits=5))
Jul13$MEAS<-paste(signif(Jul13$MEAS, digits=5))
Aug13$MEAS<-paste(signif(Aug13$MEAS, digits=5))
Sep13$MEAS<-paste(signif(Sep13$MEAS, digits=5))
Oct13$MEAS<-paste(signif(Oct13$MEAS, digits=5))
Nov13$MEAS<-paste(signif(Nov13$MEAS, digits=5))
Dec13$MEAS<-paste(signif(Dec13$MEAS, digits=5))
Jan14$MEAS<-paste(signif(Jan14$MEAS, digits=5))
Feb14$MEAS<-paste(signif(Feb14$MEAS, digits=5))
Mar14$MEAS<-paste(signif(Mar14$MEAS, digits=5))
Apr14$MEAS<-paste(signif(Apr14$MEAS, digits=5))
May14$MEAS<-paste(signif(May14$MEAS, digits=5))
Jun14$MEAS<-paste(signif(Jun14$MEAS, digits=5))
Jul14$MEAS<-paste(signif(Jul14$MEAS, digits=5))
Aug14$MEAS<-paste(signif(Aug14$MEAS, digits=5))
Sep14$MEAS<-paste(signif(Sep14$MEAS, digits=5))
Oct14$MEAS<-paste(signif(Oct14$MEAS, digits=5))
Nov14$MEAS<-paste(signif(Nov14$MEAS, digits=5))
Dec14$MEAS<-paste(signif(Dec14$MEAS, digits=5))

##joining r2 value
Dec12_r2 <- merge(Dec12,r2,by="Date",all.x = TRUE)
Jan13_r2 <- merge(Jan13,r2,by="Date",all.x = TRUE)
Feb13_r2 <- merge(Feb13,r2,by="Date",all.x = TRUE)
Mar13_r2 <- merge(Mar13,r2,by="Date",all.x = TRUE)
Apr13_r2 <- merge(Apr13,r2,by="Date",all.x = TRUE)
May13_r2 <- merge(May13,r2,by="Date",all.x = TRUE)
Jun13_r2 <- merge(Jun13,r2,by="Date",all.x = TRUE)
Jul13_r2 <- merge(Jul13,r2,by="Date",all.x = TRUE)
Aug13_r2 <- merge(Aug13,r2,by="Date",all.x = TRUE)
Sep13_r2 <- merge(Sep13,r2,by="Date",all.x = TRUE)
Oct13_r2 <- merge(Oct13,r2,by="Date",all.x = TRUE)
Nov13_r2 <- merge(Nov13,r2,by="Date",all.x = TRUE)
Dec13_r2 <- merge(Dec13,r2,by="Date",all.x = TRUE)
Jan14_r2 <- merge(Jan14,r2,by="Date",all.x = TRUE)
Feb14_r2 <- merge(Feb14,r2,by="Date",all.x = TRUE)
Mar14_r2 <- merge(Mar14,r2,by="Date",all.x = TRUE)
Apr14_r2 <- merge(Apr14,r2,by="Date",all.x = TRUE)
May14_r2 <- merge(May14,r2,by="Date",all.x = TRUE)
Jun14_r2 <- merge(Jun14,r2,by="Date",all.x = TRUE)
Jul14_r2 <- merge(Jul14,r2,by="Date",all.x = TRUE)
Aug14_r2 <- merge(Aug14,r2,by="Date",all.x = TRUE)
Sep14_r2 <- merge(Sep14,r2,by="Date",all.x = TRUE)
Oct14_r2 <- merge(Oct14,r2,by="Date",all.x = TRUE)
Nov14_r2 <- merge(Nov14,r2,by="Date",all.x = TRUE)
Dec14_r2 <- merge(Dec14,r2,by="Date",all.x = TRUE)

##Implementing decision tree
Dec12_r2$Dec12_Final_CHL <- paste(ifelse(Dec12_r2$Gain0 < .8, Dec12_r2$Dec12_CHL , Dec12_r2$Dec12_NewCHL))
Dec12_r2$Dec12_Final_CHL_note <- paste(ifelse(Dec12_r2$Gain0 < .8, "Uncorrected chl" , "Gain 0"))
Jan13_r2$Jan13_Final_CHL <- paste(ifelse(Jan13_r2$Gain0 < .8 | is.na(Jan13_r2$Gain0), Jan13_r2$Jan13_CHL , Jan13_r2$Jan13_NewCHL))
Jan13_r2$Jan13_Final_CHL_note <- paste(ifelse(Jan13_r2$Gain0 < .8 | is.na(Jan13_r2$Gain0), "Uncorrected chl" , "Gain 0"))
Feb13_r2$Feb13_Final_CHL <- paste(ifelse(Feb13_r2$Gain0 < .8 | is.na(Feb13_r2$Gain0), Feb13_r2$Feb13_CHL , Feb13_r2$Feb13_NewCHL))
Feb13_r2$Feb13_Final_CHL_note <- paste(ifelse(Feb13_r2$Gain0 < .8 | is.na(Feb13_r2$Gain0), "Uncorrected chl" , "Gain 0"))
Mar13_r2$Mar13_Final_CHL <- paste(ifelse(Mar13_r2$Gain0 < .8, Mar13_r2$Mar13_CHL , Mar13_r2$Mar13_NewCHL))
Mar13_r2$Mar13_Final_CHL_note <- paste(ifelse(Mar13_r2$Gain0 < .8, "Uncorrected chl" , "Gain 0"))
Apr13_r2$Apr13_Final_CHL <- paste(ifelse(Apr13_r2$Gain0 < .8 | is.na(Apr13_r2$Gain0), Apr13_r2$Apr13_CHL , Apr13_r2$Apr13_NewCHL))
Apr13_r2$Apr13_Final_CHL_note <- paste(ifelse(Apr13_r2$Gain0 < .8 | is.na(Apr13_r2$Gain0), "Uncorrected chl" , "Gain 0"))
May13_r2$May13_Final_CHL <- paste(ifelse(May13_r2$Gain0 < .8, May13_r2$May13_CHL , May13_r2$May13_NewCHL))
May13_r2$May13_Final_CHL_note <- paste(ifelse(May13_r2$Gain0 < .8, "Uncorrected chl" , "Gain 0"))
Jun13_r2$Jun13_Final_CHL <- paste(ifelse(Jun13_r2$Gain0 < .8, Jun13_r2$Jun13_CHL , Jun13_r2$Jun13_NewCHL))
Jun13_r2$Jun13_Final_CHL_note <- paste(ifelse(Jun13_r2$Gain0 < .8, "Uncorrected chl" , "Gain 0"))
Jul13_r2$Jul13_Final_CHL <- paste(ifelse(Jul13_r2$Date == "7/2/2013", ifelse(Jul13_r2$Jul13_CHL < 45, ifelse(Jul13_r2$Gain1 < .8, Jul13_r2$Jul13_CHL, Jul13_r2$NewCHL_gn1), ifelse(Jul13_r2$Gain10 < .8,Jul13_r2$Jul13_CHL, Jul13_r2$NewCHL_g_1)),ifelse(Jul13_r2$Gain0 < .8, Jul13_r2$Jul13_CHL , Jul13_r2$Jul13_NewCHL)))                   
Jul13_r2$Jul13_Final_CHL_note <- paste(ifelse(Jul13_r2$Date == "7/2/2013", ifelse(Jul13_r2$Jul13_CHL < 45, ifelse(Jul13_r2$Gain1 < .8, "Uncorrected chl", "Gain 1"), ifelse(Jul13_r2$Gain10 < .8,"Uncorrected chl", "Gain 10")),ifelse(Jul13_r2$Gain0 < .8, "Uncorrected chl" , "Gain 0")))                   
Aug13_r2$Aug13_Final_CHL <- paste(ifelse(Aug13_r2$CHL < 45, ifelse(Aug13_r2$Gain10 < .8, Aug13_r2$CHL, Aug13_r2$NewCHL_g_1), ifelse(Aug13_r2$Gain1 < .8, Aug13_r2$CHL, Aug13_r2$NewCHL_gn1)))
Aug13_r2$Aug13_Final_CHL_note <- paste(ifelse(Aug13_r2$CHL < 45, ifelse(Aug13_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Aug13_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Sep13_r2$Sep13_Final_CHL <- paste(ifelse(Sep13_r2$CHL < 45, ifelse(Sep13_r2$Gain10 < .8, Sep13_r2$CHL, Sep13_r2$NewCHL_g_1), ifelse(Sep13_r2$Gain1 < .8, Sep13_r2$CHL, Sep13_r2$NewCHL_gn1)))
Sep13_r2$Sep13_Final_CHL_note <- paste(ifelse(Sep13_r2$CHL < 45, ifelse(Sep13_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Sep13_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Oct13_r2$Oct13_Final_CHL <- paste(ifelse(Oct13_r2$CHL < 45, ifelse(Oct13_r2$Gain10 < .8, Oct13_r2$CHL, Oct13_r2$NewCHL_g_1), ifelse(Oct13_r2$Gain1 < .8, Oct13_r2$CHL, Oct13_r2$NewCHL_gn1)))
Oct13_r2$Oct13_Final_CHL_note <- paste(ifelse(Oct13_r2$CHL < 45, ifelse(Oct13_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Oct13_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Nov13_r2$Nov13_Final_CHL <- paste(ifelse(Nov13_r2$CHL < 45, ifelse(Nov13_r2$Gain10 < .8, Nov13_r2$CHL, Nov13_r2$NewCHL_g_1), ifelse(Nov13_r2$Gain1 < .8, Nov13_r2$CHL, Nov13_r2$NewCHL_gn1)))
Nov13_r2$Nov13_Final_CHL_note <- paste(ifelse(Nov13_r2$CHL < 45, ifelse(Nov13_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Nov13_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Dec13_r2$Dec13_Final_CHL <- paste(ifelse(Dec13_r2$CHL < 45, ifelse(Dec13_r2$Gain10 < .8, Dec13_r2$CHL, Dec13_r2$NewCHL_g_1), ifelse(Dec13_r2$Gain1 < .8, Dec13_r2$CHL, Dec13_r2$NewCHL_gn1)))
Dec13_r2$Dec13_Final_CHL_note <- paste(ifelse(Dec13_r2$CHL < 45, ifelse(Dec13_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Dec13_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Jan14_r2$Jan14_Final_CHL <- paste(ifelse(Jan14_r2$CHL < 45, ifelse(Jan14_r2$Gain10 < .8, Jan14_r2$CHL, Jan14_r2$NewCHL_g_1), ifelse(Jan14_r2$Gain1 < .8, Jan14_r2$CHL, Jan14_r2$NewCHL_gn1)))
Jan14_r2$Jan14_Final_CHL_note <- paste(ifelse(Jan14_r2$CHL < 45, ifelse(Jan14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Jan14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Feb14_r2$Feb14_Final_CHL <- paste(ifelse(Feb14_r2$CHL < 45, ifelse(Feb14_r2$Gain10 < .8, Feb14_r2$CHL, Feb14_r2$NewCHL_g_1), ifelse(Feb14_r2$Gain1 < .8, Feb14_r2$CHL, Feb14_r2$NewCHL_gn1)))
Feb14_r2$Feb14_Final_CHL_note <- paste(ifelse(Feb14_r2$CHL < 45, ifelse(Feb14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Feb14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Mar14_r2$Mar14_Final_CHL <- paste(ifelse(Mar14_r2$CHL < 45, ifelse(Mar14_r2$Gain10 < .8, Mar14_r2$CHL, Mar14_r2$NewCHL_g_1), ifelse(Mar14_r2$Gain1 < .8, Mar14_r2$CHL, Mar14_r2$NewCHL_gn1)))
Mar14_r2$Mar14_Final_CHL_note <- paste(ifelse(Mar14_r2$CHL < 45, ifelse(Mar14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Mar14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Apr14_r2$Apr14_Final_CHL <- paste(ifelse(Apr14_r2$CHL < 45, ifelse(Apr14_r2$Gain10 < .8, Apr14_r2$CHL, Apr14_r2$NewCHL_g_1), ifelse(Apr14_r2$Gain1 < .8, Apr14_r2$CHL, Apr14_r2$NewCHL_gn1)))
Apr14_r2$Apr14_Final_CHL_note <- paste(ifelse(Apr14_r2$CHL < 45, ifelse(Apr14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Apr14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
May14_r2$May14_Final_CHL <- paste(ifelse(May14_r2$CHL < 45, ifelse(May14_r2$Gain10 < .8, May14_r2$CHL, May14_r2$NewCHL_g_1), ifelse(May14_r2$Gain1 < .8, May14_r2$CHL, May14_r2$NewCHL_gn1)))
May14_r2$May14_Final_CHL_note <- paste(ifelse(May14_r2$CHL < 45, ifelse(May14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(May14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Jun14_r2$Jun14_Final_CHL <- paste(ifelse(Jun14_r2$CHL < 45, ifelse(Jun14_r2$Gain10 < .8, Jun14_r2$CHL, Jun14_r2$NewCHL_g_1), ifelse(Jun14_r2$Gain1 < .8, Jun14_r2$CHL, Jun14_r2$NewCHL_gn1)))
Jun14_r2$Jun14_Final_CHL_note <- paste(ifelse(Jun14_r2$CHL < 45, ifelse(Jun14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Jun14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Jul14_r2$Jul14_Final_CHL <- paste(ifelse(Jul14_r2$CHL < 45, ifelse(Jul14_r2$Gain10 < .8, Jul14_r2$CHL, Jul14_r2$NewCHL_g_1), ifelse(Jul14_r2$Gain1 < .8, Jul14_r2$CHL, Jul14_r2$NewCHL_gn1)))
Jul14_r2$Jul14_Final_CHL_note <- paste(ifelse(Jul14_r2$CHL < 45, ifelse(Jul14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Jul14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Aug14_r2$Final_CHL_note <- ifelse(Aug14_r2$Date == "8/28/2014",
                                  ifelse(Aug14_r2$CHL <5, 
                                         ifelse(Aug14_r2$Gain100 < .8,Aug14_r2$CHL, Aug14_r2$NewCHL_g_2), 
                                         ifelse(Aug14_r2$CHL < 45, 
                                                ifelse(Aug14_r2$Gain1 < .8, Aug14_r2$CHL, Aug14_r2$NewCHL_g_1),
                                                ifelse(Aug14_r2$Gain10 < .8, Aug14_r2$CHL, Aug14_r2$NewCHL_gn1))),
                                  ifelse(Aug14_r2$CHL < 45, 
                                         ifelse(Aug14_r2$Gain10 < .8, Aug14_r2$CHL, Aug14_r2$NewCHL_g_1),
                                         ifelse(Aug14_r2$Gain1 < .8, Aug14_r2$CHL, Aug14_r2$NewCHL_gn1)))
Aug14_r2$Final_CHL_note <- ifelse(Aug14_r2$Date == "8/28/2014",
                                  ifelse(Aug14_r2$CHL <5, 
                                         ifelse(Aug14_r2$Gain100 < .8,"Uncorrected chl", "Gain 100"), 
                                         ifelse(Aug14_r2$CHL < 45, 
                                                ifelse(Aug14_r2$Gain1 < .8, "Uncorrected chl", "Gain 10"),
                                                ifelse(Aug14_r2$Gain10 < .8, "Uncorrected chl", "Gain 1"))),
                                  ifelse(Aug14_r2$CHL < 45, 
                                         ifelse(Aug14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"),
                                         ifelse(Aug14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))
Sep14_r2$Sep14_Final_CHL <- paste(ifelse(Sep14_r2$CHL <5, ifelse(Sep14_r2$Gain100 < .8,Sep14_r2$CHL, Sep14_r2$NewCHL_g_2),ifelse(Sep14_r2$CHL < 45, ifelse(Sep14_r2$Gain1 < .8, Sep14_r2$CHL, Sep14_r2$NewCHL_g_1), ifelse(Sep14_r2$Gain10 < .8, Sep14_r2$CHL, Sep14_r2$NewCHL_gn1)))) 
Sep14_r2$Sep14_Final_CHL_note <- paste(ifelse(Sep14_r2$CHL <5, ifelse(Sep14_r2$Gain100 < .8,"Uncorrected chl", "Gain 100"),ifelse(Sep14_r2$CHL < 45, ifelse(Sep14_r2$Gain1 < .8, "Uncorrected chl", "Gain 10"), ifelse(Sep14_r2$Gain10 < .8, "Uncorrected chl", "Gain 1"))))                   
Oct14_r2$Oct14_Final_CHL <- paste(ifelse(Oct14_r2$CHL <5, ifelse(Oct14_r2$Gain100 < .8,Oct14_r2$CHL, Oct14_r2$NewCHL_g_2),ifelse(Oct14_r2$CHL < 45, ifelse(Oct14_r2$Gain1 < .8, Oct14_r2$CHL, Oct14_r2$NewCHL_g_1), ifelse(Oct14_r2$Gain10 < .8, Oct14_r2$CHL, Oct14_r2$NewCHL_gn1)))) 
Oct14_r2$Oct14_Final_CHL_note <- paste(ifelse(Oct14_r2$CHL <5, ifelse(Oct14_r2$Gain100 < .8,"Uncorrected chl", "Gain 100"),ifelse(Oct14_r2$CHL < 45, ifelse(Oct14_r2$Gain1 < .8, "Uncorrected chl", "Gain 10"), ifelse(Oct14_r2$Gain10 < .8, "Uncorrected chl", "Gain 1"))))                   
Nov14_r2$Nov14_Final_CHL <- paste(ifelse(Nov14_r2$CHL <5, ifelse(Nov14_r2$Gain100 < .8,Nov14_r2$CHL, Nov14_r2$NewCHL_g_2),ifelse(Nov14_r2$CHL < 45, ifelse(Nov14_r2$Gain1 < .8, Nov14_r2$CHL, Nov14_r2$NewCHL_g_1), ifelse(Nov14_r2$Gain10 < .8, Nov14_r2$CHL, Nov14_r2$NewCHL_gn1)))) 
Nov14_r2$Nov14_Final_CHL_note <- paste(ifelse(Nov14_r2$CHL <5, ifelse(Nov14_r2$Gain100 < .8,"Uncorrected chl", "Gain 100"),ifelse(Nov14_r2$CHL < 45, ifelse(Nov14_r2$Gain1 < .8, "Uncorrected chl", "Gain 10"), ifelse(Nov14_r2$Gain10 < .8, "Uncorrected chl", "Gain 1"))))                   
Dec14_r2$Dec14_Final_CHL <- paste(ifelse(Dec14_r2$CHL <5, ifelse(Dec14_r2$Gain100 < .8,Dec14_r2$CHL, Dec14_r2$NewCHL_g_2),ifelse(Dec14_r2$CHL < 45, ifelse(Dec14_r2$Gain1 < .8, Dec14_r2$CHL, Dec14_r2$NewCHL_g_1), ifelse(Dec14_r2$Gain10 < .8, Dec14_r2$CHL, Dec14_r2$NewCHL_gn1)))) 
Dec14_r2$Dec14_Final_CHL_note <- paste(ifelse(Dec14_r2$CHL <5, ifelse(Dec14_r2$Gain100 < .8,"Uncorrected chl", "Gain 100"),ifelse(Dec14_r2$CHL < 45, ifelse(Dec14_r2$Gain1 < .8, "Uncorrected chl", "Gain 10"), ifelse(Dec14_r2$Gain10 < .8, "Uncorrected chl", "Gain 1"))))                   

##merge all months together
a <- join(Final_CHL, Dec12_r2, by=c("MEAS", "RID"))
b <- join(a, Jan13_r2, by=c("MEAS", "RID"))
c <- join(b, Feb13_r2, by=c("MEAS", "RID"))
d <- join(c, Mar13_r2, by=c("MEAS", "RID"))
e <- join(d, Apr13_r2, by=c("MEAS", "RID"))
f <- join(e, May13_r2, by=c("MEAS", "RID"))
g <- join(f, Jun13_r2, by=c("MEAS", "RID"))
h <- join(g, Jul13_r2, by=c("MEAS", "RID"))
i <- join(h, Aug13_r2, by=c("MEAS", "RID"))
j <- join(i, Sep13_r2, by=c("MEAS", "RID"))
k <- join(j, Oct13_r2, by=c("MEAS", "RID"))
l <- join(k, Nov13_r2, by=c("MEAS", "RID"))
m <- join(l, Dec13_r2, by=c("MEAS", "RID"))
n <- join(m, Jan14_r2, by=c("MEAS", "RID"))
o <- join(n, Feb14_r2, by=c("MEAS", "RID"))
p <- join(o, Mar14_r2, by=c("MEAS", "RID"))
q <- join(p, Apr14_r2, by=c("MEAS", "RID"))
r <- join(q, May14_r2, by=c("MEAS", "RID"))
s <- join(r, Jun14_r2, by=c("MEAS", "RID"))
t <- join(s, Jul14_r2, by=c("MEAS", "RID"))
u <- join(t, Aug14_r2, by=c("MEAS", "RID"))
v <- join(u, Sep14_r2, by=c("MEAS", "RID"))
w <- join(v, Oct14_r2, by=c("MEAS", "RID"))
x <- join(w, Nov14_r2, by=c("MEAS", "RID"))
y <- join(x, Dec14_r2, by=c("MEAS", "RID"))

##subset by column names - we only need final chl here
wq <- subset(y, select=c(RID, Labels, Dec12_Final_CHL, Jan13_Final_CHL, Feb13_Final_CHL, Mar13_Final_CHL, Apr13_Final_CHL, 
                         May13_Final_CHL, Jun13_Final_CHL, Jul13_Final_CHL, Aug13_Final_CHL, Sep13_Final_CHL, 
                         Oct13_Final_CHL, Nov13_Final_CHL, Dec13_Final_CHL, Jan14_Final_CHL, Feb14_Final_CHL, 
                         Mar14_Final_CHL, Apr14_Final_CHL, May14_Final_CHL, Jun14_Final_CHL, Jul14_Final_CHL,
                         Aug14_Final_CHL, Sep14_Final_CHL, Oct14_Final_CHL, Nov14_Final_CHL, Dec14_Final_CHL))

wq2 <- subset(y, select=c(RID, Labels, Dec12_Final_CHL, Dec12_Final_CHL_note, Jan13_Final_CHL, Jan13_Final_CHL_note, Feb13_Final_CHL, Feb13_Final_CHL_note, Mar13_Final_CHL, Mar13_Final_CHL_note, Apr13_Final_CHL, Apr13_Final_CHL_note, 
                         May13_Final_CHL, May13_Final_CHL_note, Jun13_Final_CHL, Jun13_Final_CHL_note, Jul13_Final_CHL, Jul13_Final_CHL_note, Aug13_Final_CHL, Aug13_Final_CHL_note, Sep13_Final_CHL, Sep13_Final_CHL_note, 
                         Oct13_Final_CHL, Oct13_Final_CHL_note, Nov13_Final_CHL, Nov13_Final_CHL_note, Dec13_Final_CHL, Dec13_Final_CHL_note, Jan14_Final_CHL, Jan14_Final_CHL_note, Feb14_Final_CHL, Feb14_Final_CHL_note, 
                         Mar14_Final_CHL, Mar14_Final_CHL_note, Apr14_Final_CHL, Apr14_Final_CHL_note, May14_Final_CHL, May14_Final_CHL_note, Jun14_Final_CHL, Jun14_Final_CHL_note, Jul14_Final_CHL, Jul14_Final_CHL_note,
                         Aug14_Final_CHL, Aug14_Final_CHL_note, Sep14_Final_CHL, Sep14_Final_CHL_note, Oct14_Final_CHL, Oct14_Final_CHL_note, Nov14_Final_CHL, Nov14_Final_CHL_note, Dec14_Final_CHL, Dec14_Final_CHL_note))

write.csv(wq, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Final_CHL_All.csv")

write.csv(wq2, "X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_Final_CHL_All_with_notes.csv")
