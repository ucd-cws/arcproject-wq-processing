


#Opening r^2 and monthly files
#####
r2 <- read.csv("X:/ArcProject/Arc_Heatmaps/Arc_wqt_snapped_corrected/Arc_r2.csv")
Dec12 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Dec2012_gn0_wqtchl.csv")
Jan13 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Jan2013_gn0_wqtchl.csv")
Feb13 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Feb2013_gn0_wqtchl.csv")
Mar13 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Mar2013_gn0_wqtchl.csv")
Apr13 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Apr2013_gn0_wqtchl.csv")
May13 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_May2013_gn0_wqtchl.csv")
Jun13 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Jun2013_gn0_wqtchl.csv")
Jul13 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Jul2013_gn0_gn1_gn10_wqtchl.csv")
Aug13 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Aug2013_gn1_gn10_wqtchl.csv")
Sep13 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Sep2013_gn1_gn10_wqtchl.csv")
Oct13 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Oct2013_gn1_gn10_wqtchl.csv")
Nov13 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Nov2013_gn1_gn10_wqtchl.csv")
Dec13 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Dec2013_gn1_gn10_wqtchl.csv")
Jan14 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Jan2014_gn1_gn10_wqtchl.csv")
Feb14 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Feb2014_gn1_gn10_wqtchl.csv")
Mar14 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Mar2014_gn1_gn10_wqtchl.csv")
Apr14 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Apr2014_gn1_gn10_wqtchl.csv")
May14 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_May2014_gn1_gn10_wqtchl.csv")
Jun14 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Jun2014_gn1_gn10_wqtchl.csv")
Jul14 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Jul2014_gn1_gn10_wqtchl.csv")
Aug14 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Aug2014_gn1_gn10_gn100_wqtchl.csv")
Sep14 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Sep2014_gn1_gn10_gn100_wqtchl.csv")
Oct14 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Oct2014_gn1_gn10_gn100_wqtchl.csv")
Nov14 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Nov2014_gn1_gn10_gn100_wqtchl.csv")
Dec14 <- read.csv("X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Dec2014_gn1_gn10_gn100_wqtchl.csv")

#Change column names
colnames(Dec12)[colnames(Dec12) == "NewCHL"] <- "CHL_gn0"
colnames(Jan13)[colnames(Jan13) == "NewCHL"] <- "CHL_gn0"
colnames(Feb13)[colnames(Feb13) == "NewCHL"] <- "CHL_gn0"
colnames(Mar13)[colnames(Mar13) == "NewCHL"] <- "CHL_gn0"
colnames(Apr13)[colnames(Apr13) == "NewCHL"] <- "CHL_gn0"
colnames(May13)[colnames(May13) == "NewCHL"] <- "CHL_gn0"
colnames(Jun13)[colnames(Jun13) == "NewCHL"] <- "CHL_gn0"
colnames(Jul13)[colnames(Jul13) == "NewCHL"] <- "CHL_gn0"
colnames(Jul13)[colnames(Jul13) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Jul13)[colnames(Jul13) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Aug13)[colnames(Aug13) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Aug13)[colnames(Aug13) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Sep13)[colnames(Sep13) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Sep13)[colnames(Sep13) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Oct13)[colnames(Oct13) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Oct13)[colnames(Oct13) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Nov13)[colnames(Nov13) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Nov13)[colnames(Nov13) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Dec13)[colnames(Dec13) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Dec13)[colnames(Dec13) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Jan14)[colnames(Jan14) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Jan14)[colnames(Jan14) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Feb14)[colnames(Feb14) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Feb14)[colnames(Feb14) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Mar14)[colnames(Mar14) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Mar14)[colnames(Mar14) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Apr14)[colnames(Apr14) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Apr14)[colnames(Apr14) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(May14)[colnames(May14) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(May14)[colnames(May14) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Jun14)[colnames(Jun14) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Jun14)[colnames(Jun14) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Jul14)[colnames(Jul14) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Jul14)[colnames(Jul14) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Aug14)[colnames(Aug14) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Aug14)[colnames(Aug14) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Aug14)[colnames(Aug14) == "NewCHL_gn100"] <- "CHL_gn100"
colnames(Sep14)[colnames(Sep14) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Sep14)[colnames(Sep14) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Sep14)[colnames(Sep14) == "NewCHL_gn100"] <- "CHL_gn100"
colnames(Oct14)[colnames(Oct14) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Oct14)[colnames(Oct14) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Oct14)[colnames(Oct14) == "NewCHL_gn100"] <- "CHL_gn100"
colnames(Nov14)[colnames(Nov14) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Nov14)[colnames(Nov14) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Nov14)[colnames(Nov14) == "NewCHL_gn100"] <- "CHL_gn100"
colnames(Dec14)[colnames(Dec14) == "NewCHL_gn1"] <- "CHL_gn1"
colnames(Dec14)[colnames(Dec14) == "NewCHL_gn10"] <- "CHL_gn10"
colnames(Dec14)[colnames(Dec14) == "NewCHL_gn100"] <- "CHL_gn100"

#Merging monthly file with r^2 values
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

#Implementing decision tree
Dec12_r2$Final_CHL <- paste(ifelse(Dec12_r2$Gain0 < .8, Dec12_r2$CHL , Dec12_r2$CHL_gn0))
Dec12_r2$Final_CHL_note <- paste(ifelse(Dec12_r2$Gain0 < .8, "Uncorrected chl" , "Gain 0"))
Jan13_r2$Final_CHL <- paste(ifelse(Jan13_r2$Gain0 < .8 | is.na(Jan13_r2$Gain0), Jan13_r2$CHL , Jan13_r2$CHL_gn0))
Jan13_r2$Final_CHL_note <- paste(ifelse(Jan13_r2$Gain0 < .8 | is.na(Jan13_r2$Gain0), "Uncorrected chl" , "Gain 0"))
Feb13_r2$Final_CHL <- paste(ifelse(Feb13_r2$Gain0 < .8 | is.na(Feb13_r2$Gain0), Feb13_r2$CHL , Feb13_r2$CHL_gn0))
Feb13_r2$Final_CHL_note <- paste(ifelse(Feb13_r2$Gain0 < .8 | is.na(Feb13_r2$Gain0), "Uncorrected chl" , "Gain 0"))
Mar13_r2$Final_CHL <- paste(ifelse(Mar13_r2$Gain0 < .8, Mar13_r2$CHL , Mar13_r2$CHL_gn0))
Mar13_r2$Final_CHL_note <- paste(ifelse(Mar13_r2$Gain0 < .8, "Uncorrected chl" , "Gain 0"))
Apr13_r2$Final_CHL <- paste(ifelse(Apr13_r2$Gain0 < .8 | is.na(Apr13_r2$Gain0), Apr13_r2$CHL , Apr13_r2$CHL_gn0))
Apr13_r2$Final_CHL_note <- paste(ifelse(Apr13_r2$Gain0 < .8 | is.na(Apr13_r2$Gain0), "Uncorrected chl" , "Gain 0"))
May13_r2$Final_CHL <- paste(ifelse(May13_r2$Gain0 < .8, May13_r2$CHL , May13_r2$CHL_gn0))
May13_r2$Final_CHL_note <- paste(ifelse(May13_r2$Gain0 < .8, "Uncorrected chl" , "Gain 0"))
Jun13_r2$Final_CHL <- paste(ifelse(Jun13_r2$Gain0 < .8, Jun13_r2$CHL , Jun13_r2$CHL_gn0))
Jun13_r2$Final_CHL_note <- paste(ifelse(Jun13_r2$Gain0 < .8, "Uncorrected chl" , "Gain 0"))
Jul13_r2$Final_CHL <- paste( ifelse(Jul13_r2$Date == "7/2/2013", ifelse(Jul13_r2$CHL < 45,ifelse(Jul13_r2$Gain1 < .8, Jul13_r2$CHL, Jul13_r2$CHL_gn1),ifelse(Jul13_r2$Gain10 < .8,Jul13_r2$CHL, Jul13_r2$CHL_gn10)),ifelse(Jul13_r2$Gain0 < .8, Jul13_r2$CHL , Jul13_r2$CHL_gn0)))                   
Jul13_r2$Final_CHL_note <- paste(ifelse(Jul13_r2$Date == "7/2/2013", ifelse(Jul13_r2$CHL < 45, ifelse(Jul13_r2$Gain1 < .8, "Uncorrected chl", "Gain 1"), ifelse(Jul13_r2$Gain10 < .8,"Uncorrected chl", "Gain 10")),ifelse(Jul13_r2$Gain0 < .8, "Uncorrected chl" , "Gain 0")))                   
Aug13_r2$Final_CHL <- paste(ifelse(Aug13_r2$CHL < 45, ifelse(Aug13_r2$Gain10 < .8, Aug13_r2$CHL, Aug13_r2$CHL_gn10), ifelse(Aug13_r2$Gain1 < .8, Aug13_r2$CHL, Aug13_r2$CHL_gn1)))
Aug13_r2$Final_CHL_note <- paste(ifelse(Aug13_r2$CHL < 45, ifelse(Aug13_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Aug13_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Sep13_r2$Final_CHL <- paste(ifelse(Sep13_r2$CHL < 45, ifelse(Sep13_r2$Gain10 < .8, Sep13_r2$CHL, Sep13_r2$CHL_gn10), ifelse(Sep13_r2$Gain1 < .8, Sep13_r2$CHL, Sep13_r2$CHL_gn1)))
Sep13_r2$Final_CHL_note <- paste(ifelse(Sep13_r2$CHL < 45, ifelse(Sep13_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Sep13_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Oct13_r2$Final_CHL <- paste(ifelse(Oct13_r2$CHL < 45, ifelse(Oct13_r2$Gain10 < .8, Oct13_r2$CHL, Oct13_r2$CHL_gn10), ifelse(Oct13_r2$Gain1 < .8, Oct13_r2$CHL, Oct13_r2$CHL_gn1)))
Oct13_r2$Final_CHL_note <- paste(ifelse(Oct13_r2$CHL < 45, ifelse(Oct13_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Oct13_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Nov13_r2$Final_CHL <- paste(ifelse(Nov13_r2$CHL < 45, ifelse(Nov13_r2$Gain10 < .8, Nov13_r2$CHL, Nov13_r2$CHL_gn10), ifelse(Nov13_r2$Gain1 < .8, Nov13_r2$CHL, Nov13_r2$CHL_gn1)))
Nov13_r2$Final_CHL_note <- paste(ifelse(Nov13_r2$CHL < 45, ifelse(Nov13_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Nov13_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Dec13_r2$Final_CHL <- paste(ifelse(Dec13_r2$CHL < 45, ifelse(Dec13_r2$Gain10 < .8, Dec13_r2$CHL, Dec13_r2$CHL_gn10), ifelse(Dec13_r2$Gain1 < .8, Dec13_r2$CHL, Dec13_r2$CHL_gn1)))
Dec13_r2$Final_CHL_note <- paste(ifelse(Dec13_r2$CHL < 45, ifelse(Dec13_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Dec13_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Jan14_r2$Final_CHL <- paste(ifelse(Jan14_r2$CHL < 45, ifelse(Jan14_r2$Gain10 < .8, Jan14_r2$CHL, Jan14_r2$CHL_gn10), ifelse(Jan14_r2$Gain1 < .8, Jan14_r2$CHL, Jan14_r2$CHL_gn1)))
Jan14_r2$Final_CHL_note <- paste(ifelse(Jan14_r2$CHL < 45, ifelse(Jan14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Jan14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Feb14_r2$Final_CHL <- paste(ifelse(Feb14_r2$CHL < 45, ifelse(Feb14_r2$Gain10 < .8, Feb14_r2$CHL, Feb14_r2$CHL_gn10), ifelse(Feb14_r2$Gain1 < .8, Feb14_r2$CHL, Feb14_r2$CHL_gn1)))
Feb14_r2$Final_CHL_note <- paste(ifelse(Feb14_r2$CHL < 45, ifelse(Feb14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Feb14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Mar14_r2$Final_CHL <- paste(ifelse(Mar14_r2$CHL < 45, ifelse(Mar14_r2$Gain10 < .8, Mar14_r2$CHL, Mar14_r2$CHL_gn10), ifelse(Mar14_r2$Gain1 < .8, Mar14_r2$CHL, Mar14_r2$CHL_gn1)))
Mar14_r2$Final_CHL_note <- paste(ifelse(Mar14_r2$CHL < 45, ifelse(Mar14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Mar14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Apr14_r2$Final_CHL <- paste(ifelse(Apr14_r2$CHL < 45, ifelse(Apr14_r2$Gain10 < .8, Apr14_r2$CHL, Apr14_r2$CHL_gn10), ifelse(Apr14_r2$Gain1 < .8, Apr14_r2$CHL, Apr14_r2$CHL_gn1)))
Apr14_r2$Final_CHL_note <- paste(ifelse(Apr14_r2$CHL < 45, ifelse(Apr14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Apr14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
May14_r2$Final_CHL <- paste(ifelse(May14_r2$CHL < 45, ifelse(May14_r2$Gain10 < .8, May14_r2$CHL, May14_r2$CHL_gn10), ifelse(May14_r2$Gain1 < .8, May14_r2$CHL, May14_r2$CHL_gn1)))
May14_r2$Final_CHL_note <- paste(ifelse(May14_r2$CHL < 45, ifelse(May14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(May14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Jun14_r2$Final_CHL <- paste(ifelse(Jun14_r2$CHL < 45, ifelse(Jun14_r2$Gain10 < .8, Jun14_r2$CHL, Jun14_r2$CHL_gn10), ifelse(Jun14_r2$Gain1 < .8, Jun14_r2$CHL, Jun14_r2$CHL_gn1)))
Jun14_r2$Final_CHL_note <- paste(ifelse(Jun14_r2$CHL < 45, ifelse(Jun14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Jun14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Jul14_r2$Final_CHL <- paste(ifelse(Jul14_r2$CHL < 45, ifelse(Jul14_r2$Gain10 < .8, Jul14_r2$CHL, Jul14_r2$CHL_gn10), ifelse(Jul14_r2$Gain1 < .8, Jul14_r2$CHL, Jul14_r2$CHL_gn1)))
Jul14_r2$Final_CHL_note <- paste(ifelse(Jul14_r2$CHL < 45, ifelse(Jul14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"), ifelse(Jul14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))                      
Aug14_r2$Final_CHL <- ifelse(Aug14_r2$Date == "8/28/2014",
                                  ifelse(Aug14_r2$CHL <5, 
                                         ifelse(Aug14_r2$Gain100 < .8,Aug14_r2$CHL, Aug14_r2$CHL_gn100), 
                                         ifelse(Aug14_r2$CHL < 45, 
                                                ifelse(Aug14_r2$Gain1 < .8, Aug14_r2$CHL, Aug14_r2$CHL_gn10),
                                                ifelse(Aug14_r2$Gain10 < .8, Aug14_r2$CHL, Aug14_r2$CHL_gn1))),
                                  ifelse(Aug14_r2$CHL < 45, 
                                         ifelse(Aug14_r2$Gain10 < .8, Aug14_r2$CHL, Aug14_r2$CHL_gn10),
                                         ifelse(Aug14_r2$Gain1 < .8, Aug14_r2$CHL, Aug14_r2$CHL_gn1)))
Aug14_r2$Final_CHL_note <- ifelse(Aug14_r2$Date == "8/28/2014",
                                  ifelse(Aug14_r2$CHL <5, 
                                         ifelse(Aug14_r2$Gain100 < .8,"Uncorrected chl", "Gain 100"), 
                                         ifelse(Aug14_r2$CHL < 45, 
                                                ifelse(Aug14_r2$Gain1 < .8, "Uncorrected chl", "Gain 10"),
                                                ifelse(Aug14_r2$Gain10 < .8, "Uncorrected chl", "Gain 1"))),
                                  ifelse(Aug14_r2$CHL < 45, 
                                         ifelse(Aug14_r2$Gain10 < .8, "Uncorrected chl", "Gain 10"),
                                         ifelse(Aug14_r2$Gain1 < .8, "Uncorrected chl", "Gain 1")))
Sep14_r2$Final_CHL <- paste(ifelse(Sep14_r2$CHL <5, ifelse(Sep14_r2$Gain100 < .8,Sep14_r2$CHL, Sep14_r2$CHL_gn100),ifelse(Sep14_r2$CHL < 45, ifelse(Sep14_r2$Gain1 < .8, Sep14_r2$CHL, Sep14_r2$CHL_gn10), ifelse(Sep14_r2$Gain10 < .8, Sep14_r2$CHL, Sep14_r2$CHL_gn1)))) 
Sep14_r2$Final_CHL_note <- paste(ifelse(Sep14_r2$CHL <5, ifelse(Sep14_r2$Gain100 < .8,"Uncorrected chl", "Gain 100"),ifelse(Sep14_r2$CHL < 45, ifelse(Sep14_r2$Gain1 < .8, "Uncorrected chl", "Gain 10"), ifelse(Sep14_r2$Gain10 < .8, "Uncorrected chl", "Gain 1"))))                   
Oct14_r2$Final_CHL <- paste(ifelse(Oct14_r2$CHL <5, ifelse(Oct14_r2$Gain100 < .8,Oct14_r2$CHL, Oct14_r2$CHL_gn100),ifelse(Oct14_r2$CHL < 45, ifelse(Oct14_r2$Gain1 < .8, Oct14_r2$CHL, Oct14_r2$CHL_gn10), ifelse(Oct14_r2$Gain10 < .8, Oct14_r2$CHL, Oct14_r2$CHL_gn1)))) 
Oct14_r2$Final_CHL_note <- paste(ifelse(Oct14_r2$CHL <5, ifelse(Oct14_r2$Gain100 < .8,"Uncorrected chl", "Gain 100"),ifelse(Oct14_r2$CHL < 45, ifelse(Oct14_r2$Gain1 < .8, "Uncorrected chl", "Gain 10"), ifelse(Oct14_r2$Gain10 < .8, "Uncorrected chl", "Gain 1"))))                   
Nov14_r2$Final_CHL <- paste(ifelse(Nov14_r2$CHL <5, ifelse(Nov14_r2$Gain100 < .8,Nov14_r2$CHL, Nov14_r2$CHL_gn100),ifelse(Nov14_r2$CHL < 45, ifelse(Nov14_r2$Gain1 < .8, Nov14_r2$CHL, Nov14_r2$CHL_gn10), ifelse(Nov14_r2$Gain10 < .8, Nov14_r2$CHL, Nov14_r2$CHL_gn1)))) 
Nov14_r2$Final_CHL_note <- paste(ifelse(Nov14_r2$CHL <5, ifelse(Nov14_r2$Gain100 < .8,"Uncorrected chl", "Gain 100"),ifelse(Nov14_r2$CHL < 45, ifelse(Nov14_r2$Gain1 < .8, "Uncorrected chl", "Gain 10"), ifelse(Nov14_r2$Gain10 < .8, "Uncorrected chl", "Gain 1"))))                   
Dec14_r2$Final_CHL <- paste(ifelse(Dec14_r2$CHL <5, ifelse(Dec14_r2$Gain100 < .8,Dec14_r2$CHL, Dec14_r2$CHL_gn100),ifelse(Dec14_r2$CHL < 45, ifelse(Dec14_r2$Gain1 < .8, Dec14_r2$CHL, Dec14_r2$CHL_gn10), ifelse(Dec14_r2$Gain10 < .8, Dec14_r2$CHL, Dec14_r2$CHL_gn1)))) 
Dec14_r2$Final_CHL_note <- paste(ifelse(Dec14_r2$CHL <5, ifelse(Dec14_r2$Gain100 < .8,"Uncorrected chl", "Gain 100"),ifelse(Dec14_r2$CHL < 45, ifelse(Dec14_r2$Gain1 < .8, "Uncorrected chl", "Gain 10"), ifelse(Dec14_r2$Gain10 < .8, "Uncorrected chl", "Gain 1"))))                   


#Saving files

write.csv(Dec12_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Dec2012_FinalChl_w_note.csv")
write.csv(Jan13_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Jan2013_FinalChl_w_note.csv")
write.csv(Feb13_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Feb2013_FinalChl_w_note.csv")
write.csv(Mar13_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Mar2013_FinalChl_w_note.csv")
write.csv(Apr13_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Apr2013_FinalChl_w_note.csv")
write.csv(May13_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_May2013_FinalChl_w_note.csv")
write.csv(Jun13_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Jun2013_FinalChl_w_note.csv")
write.csv(Jul13_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Jul2013_FinalChl_w_note.csv")
write.csv(Aug13_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Aug2013_FinalChl_w_note.csv")
write.csv(Sep13_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Sep2013_FinalChl_w_note.csv")
write.csv(Oct13_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Oct2013_FinalChl_w_note.csv")
write.csv(Nov13_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Nov2013_FinalChl_w_note.csv")
write.csv(Dec13_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Dec2013_FinalChl_w_note.csv")
write.csv(Jan14_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Jan2014_FinalChl_w_note.csv")
write.csv(Feb14_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Feb2014_FinalChl_w_note.csv")
write.csv(Mar14_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Mar2014_FinalChl_w_note.csv")
write.csv(Apr14_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Apr2014_FinalChl_w_note.csv")
write.csv(May14_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_May2014_FinalChl_w_note.csv")
write.csv(Jun14_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Jun2014_FinalChl_w_note.csv")
write.csv(Jul14_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Jul2014_FinalChl_w_note.csv")
write.csv(Aug14_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Aug2014_FinalChl_w_note.csv")
write.csv(Sep14_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Sep2014_FinalChl_w_note.csv")
write.csv(Oct14_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Oct2014_FinalChl_w_note.csv")
write.csv(Nov14_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Nov2014_FinalChl_w_note.csv")
write.csv(Dec14_r2, "X:/ArcProject/Arc_Heatmaps/CorrectedFiles/Arc_Dec2014_FinalChl_w_note.csv")

